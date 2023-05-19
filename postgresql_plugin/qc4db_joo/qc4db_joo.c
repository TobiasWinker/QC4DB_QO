#include "postgres.h"
#include <limits.h>
#include <stdint.h>

#include "port.h" // needed for magic number (version control)
#include "utils/guc.h"
#include <arpa/inet.h>
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

#include "nodes/pathnodes.h"
#include "nodes/pg_list.h"
#include "optimizer/pathnode.h"
#include "optimizer/paths.h"
#include "executor/executor.h"
#include "commands/explain.h"
#include <stdio.h>

PG_MODULE_MAGIC;

void _PG_init(void);

/* Original Hook */
static join_search_hook_type orginal_join_search = NULL;

// list all names of relations in rel
static void printNames(PlannerInfo *root, RelOptInfo *rel) {
  int x;
  printf("Relations for %p: ",rel);
  x = -1;
  while ((x = bms_next_member(rel->relids, x)) >= 0) {
    printf("%s ",root->simple_rte_array[x]->eref->aliasname);
  }
  printf("\n");
}

static char *toName(PlannerInfo *root, RelOptInfo *rel) {
  int x = bms_next_member(rel->relids, -1);
  if (x < 0) {
    return "Invalid";
  }
  return root->simple_rte_array[x]->eref->aliasname;
}
/*
Recursively iterate all subsets depth first and collect the cardinalities.

Example for set 'abcd':
ab,abc,abcd,abd,ac,acd,ad,bc,bcd,bd,cd
*/
static int64_t *iterateCombinations(PlannerInfo *root, List *rels, int cIndex, RelOptInfo *cJoin, int64_t *cardinalities) {
  ListCell *lc;
  RelOptInfo *newJoin, *lJoin;
  int index;
  if (cIndex > rels->length) {
    return cardinalities;
  }
  for_each_from(lc, rels, cIndex) {
    lJoin = lfirst(lc);
    index = foreach_current_index(lc);
    if (cIndex == 0) {
      // first table in join
      newJoin = lJoin;
    } else {
      // make join from this and previous join
      newJoin = make_join_rel(root, lJoin, cJoin);
      set_cheapest(newJoin);
      // save cardinality and increase pointer
      *cardinalities = newJoin->rows;
      cardinalities++;
    }
    cardinalities = iterateCombinations(root, rels, index + 1, newJoin, cardinalities);
  }
  return cardinalities;
}

/*
 * send format :
 * table names, separated by semicolon, followed by a 0-byte at the end
 * followed by an array of int64 of length "(1 << number_of_relations) - 1 - number_of_relations" containing the estimated costs
 *
 * receive format :
 * array of int16 of length "(number_of_relations - 1) * 2"
 */
#define port 17342
static RelOptInfo *quantum_join_search(PlannerInfo *root, int levels_needed, List *initial_rels) {
  int sock = 0;
  int conn_fd = 0;

  int message_size = 0;
  char *message = NULL;

  int weights_size = 0;
  int64_t *weights = NULL;

  int16_t *join_order_response = NULL;
  char *join_order_response_tmp = NULL;
  int join_order_response_size = 0;
  int join_order_response_remaining = 0;

  int i = 0;
  int j = 0;
  int number_of_relations = 0;
  struct sockaddr_in serv_addr;
  ListCell *lc = NULL;
  RelOptInfo **rels = NULL;
  RelOptInfo *res = NULL;

  if ((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
    printf("\n Socket creation error \n");
    goto _error;
  }
  serv_addr.sin_family = AF_INET;
  serv_addr.sin_port = htons(port);
  if (inet_pton(AF_INET, "127.0.0.1", &serv_addr.sin_addr) <= 0) {
    printf("\nInvalid address/ Address not supported \n");
    goto _error;
  }
  if ((conn_fd = connect(sock, (struct sockaddr *)&serv_addr, sizeof(serv_addr))) < 0) {
    printf("\nConnection Failed \n");
    goto _error;
  }
  // connection established
  number_of_relations = initial_rels->length;
  if (!number_of_relations) {
    printf("the function 'quantum_join_search' must not be called with zero inputs to join\n");
    goto _error;
  }
  rels = palloc(sizeof(RelOptInfo **) * ((number_of_relations - 1) * 2 + 1));
  i = 0;
  foreach (lc, initial_rels) {
    rels[i] = lfirst(lc);
    bms_next_member(rels[i]->relids, -1);
    message_size += snprintf(NULL, 0, "%s;", toName(root, rels[i]));
    i++;
  }
  weights_size = sizeof(int64_t) * ((1 << number_of_relations) - 1 - number_of_relations);
  weights = palloc(weights_size);
  
  i = iterateCombinations(root, initial_rels, 0, NULL, weights) - weights;
  // forget all created RelOptInfos. We assume non are created before, thus set length to 0
  root->join_rel_list = list_truncate(root->join_rel_list,0);
  for(i=0; i< weights_size; i++) {
    //weights[i]=1;
  }
  message = palloc(message_size + weights_size);
  for (i = 0; i < number_of_relations; i++) {
    j += sprintf(message + j, "%s;", toName(root, rels[i]));
  }
  printf("Relations to join: %s\n",message);
  message[message_size - 1] = 0;
  memcpy(message + message_size, weights, weights_size);
  send(sock, message, message_size + weights_size, 0);
  join_order_response_size = sizeof(int16_t) * (number_of_relations - 1) * 2;
  join_order_response = palloc(join_order_response_size);
  join_order_response_tmp = (char *)join_order_response;
  join_order_response_remaining = join_order_response_size;
  while (join_order_response_remaining > 0) {
    i = read(sock, join_order_response_tmp, join_order_response_remaining);
    if (i < 0) {
      printf("Connection error ... too few bytes\n");
      goto _error;
    }
    if (i == 0) {
      printf("Connection closed by remote\n");
      goto _error;
    }
    join_order_response_tmp += i;
    join_order_response_remaining -= i;
  }

  for (i = 0; i < number_of_relations - 1; i++) {
    printf("Joining %d and %d ...", join_order_response[i * 2], join_order_response[i * 2 + 1]);
    rels[number_of_relations + i] = make_join_rel(root, rels[join_order_response[i * 2]], rels[join_order_response[i * 2 + 1]]);
    set_cheapest(rels[number_of_relations + i]);
  }
  printf("Join complete\n");

  // Cleanup
  close(sock);
  res = rels[(number_of_relations - 1) * 2];
  pfree(message);
  pfree(join_order_response);
  pfree(rels);
  pfree(weights);
  return res;
  //  return standard_join_search(root, levels_needed, initial_rels);
_error:
  printf("\033[0;31m");  // red
  printf("An error occurred. Fallback to standard_join_search");
  printf("\033[0m\n");  // reset
  close(sock);
  pfree(message);
  pfree(join_order_response);
  pfree(rels);
  pfree(weights);
  return(orginal_join_search(root, levels_needed, initial_rels));
} 

/*
 * Module Load Callback
 */
void _PG_init(void) {
  orginal_join_search = join_search_hook;
  printf("\033[0;36m");  // cyan
  printf("\n-----------------------------------------------\n");
  printf("Running the qc4db joo plugin. Join order request will be redirected to port 17342.\n");
  printf("-----------------------------------------------\n");
  printf("\033[0m\n");
  join_search_hook = quantum_join_search;
}
