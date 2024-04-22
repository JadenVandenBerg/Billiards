#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "phylib.h"

/*
 *  Makes a new still ball
 */
phylib_object *phylib_new_still_ball(unsigned char number, phylib_coord *pos) {

  phylib_object *object = NULL;

  // Malloc and check for failure
  object = (phylib_object *)malloc(sizeof(phylib_object));
  if (object == NULL) {
    return NULL;
  }

  object->type = PHYLIB_STILL_BALL;
  object->obj.still_ball.number = number;
  object->obj.still_ball.pos.x = pos->x;
  object->obj.still_ball.pos.y = pos->y;

  return object;
}

/*
 *  Makes a new rolling ball
 */
phylib_object *phylib_new_rolling_ball(unsigned char number, phylib_coord *pos,
                                       phylib_coord *vel, phylib_coord *acc) {
  phylib_object *object = NULL;

  // Malloc and check for failure
  object = malloc(sizeof(phylib_object));
  if (object == NULL) {
    return NULL;
  }

  object->type = PHYLIB_ROLLING_BALL;
  object->obj.rolling_ball.number = number;
  object->obj.rolling_ball.pos.x = pos->x;
  object->obj.rolling_ball.pos.y = pos->y;
  object->obj.rolling_ball.vel.x = vel->x;
  object->obj.rolling_ball.vel.y = vel->y;
  object->obj.rolling_ball.acc.x = acc->x;
  object->obj.rolling_ball.acc.y = acc->y;

  return object;
}

/*
 *  Makes a new hole
 */
phylib_object *phylib_new_hole(phylib_coord *pos) {
  phylib_object *object = NULL;

  // Malloc and check for failure
  object = malloc(sizeof(phylib_object));
  if (object == NULL) {
    return NULL;
  }

  object->type = PHYLIB_HOLE;
  object->obj.hole.pos.x = pos->x;
  object->obj.hole.pos.y = pos->y;

  return object;
}

/*
 *  Makes a new hcushion
 */
phylib_object *phylib_new_hcushion(double y) {
  phylib_object *object = NULL;

  // Malloc and check for failure
  object = malloc(sizeof(phylib_object));
  if (object == NULL) {
    return NULL;
  }

  object->type = PHYLIB_HCUSHION;
  object->obj.hcushion.y = y;

  return object;
}

/*
 *  Makes a new vcushion
 */
phylib_object *phylib_new_vcushion(double x) {
  phylib_object *object = NULL;

  // Malloc and check for failure
  object = malloc(sizeof(phylib_object));
  if (object == NULL) {
    return NULL;
  }

  object->type = PHYLIB_VCUSHION;
  object->obj.vcushion.x = x;

  return object;
}

/*
 *  Makes a new table
 */
phylib_table *phylib_new_table(void) {
  phylib_table *table = NULL;

  table = (phylib_table *)malloc(sizeof(phylib_table));
  if (table == NULL) {
    return NULL;
  }

  for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++) {
    table->object[i] = NULL;
  }

  table->time = 0.0;
  phylib_add_object(table, phylib_new_hcushion(0.0));
  phylib_add_object(table, phylib_new_hcushion(PHYLIB_TABLE_LENGTH));
  phylib_add_object(table, phylib_new_vcushion(0.0));
  phylib_add_object(table, phylib_new_vcushion(PHYLIB_TABLE_WIDTH));

  for (double x = 0; x <= 1; x++) {
    for (double y = 0; y <= 1; y = y + 0.5) {
      phylib_coord coord;

      coord.x = x * PHYLIB_TABLE_WIDTH;
      coord.y = y * PHYLIB_TABLE_LENGTH;
      phylib_add_object(table, phylib_new_hole(&coord));
    }
  }

  for (int x = 10; x < PHYLIB_MAX_OBJECTS; x++) {
    phylib_add_object(table, NULL);
  }

  return table;
}

/*
 *  Makes a copy of an existing table
 */
phylib_table *phylib_copy_table(phylib_table *table) {
  phylib_table *newTable = malloc(sizeof(phylib_table));

  if (newTable == NULL) {
    return NULL;
  }

  newTable->time = table->time;

  for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++) {
    newTable->object[i] = NULL;
    phylib_copy_object(&(newTable->object[i]), &(table->object[i]));
  }

  return newTable;
}

/*
 *  Makes a copy of an existing object
 */
void phylib_copy_object(phylib_object **dest, phylib_object **src) {
  if (src == NULL || *src == NULL) {
    (*dest) = NULL;
    return;
  }

  *dest = (phylib_object *)malloc(sizeof(phylib_object));
  if (*dest == NULL) {
    return;
  }

  memcpy(*dest, *src, sizeof(phylib_object));
}

/*
 *  Adds an object to the first available null space in the table
 */
void phylib_add_object(phylib_table *table, phylib_object *object) {
  for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++) {
    if (table->object[i] == NULL) {
      table->object[i] = object;
      return;
    }
  }
}

/*
 *  Frees the table
 */
void phylib_free_table(phylib_table *table) {
  for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++) {
    if (table->object[i] != NULL) {
      free(table->object[i]);
    }
  }

  free(table);
}

/*
 *  Returns the subtraction of two coords in form x1 - x2, y1 - y2
 */
phylib_coord phylib_sub(phylib_coord c1, phylib_coord c2) {
  phylib_coord coord;
  coord.x = c1.x - c2.x;
  coord.y = c1.y - c2.y;

  return coord;
}

/*
 *  Returns the length of a coord in relation to (0,0)
 */
double phylib_length(phylib_coord c) { return sqrt((c.x * c.x) + (c.y * c.y)); }

/*
 *  Takes the dot product of 2 coords
 */
double phylib_dot_product(phylib_coord a, phylib_coord b) {
  return (a.x * b.x + a.y * b.y);
}

/*
 * Calculates the distance between two objects
 * Obj1 is a rolling ball
 */
double phylib_distance(phylib_object *obj1, phylib_object *obj2) {
  if (obj1 == NULL || obj2 == NULL || obj1->type != PHYLIB_ROLLING_BALL) {
    return -1;
  }

  phylib_coord pos1 = obj1->obj.rolling_ball.pos;

  if (obj2->type == PHYLIB_STILL_BALL) {
    phylib_coord subbed = phylib_sub(pos1, obj2->obj.still_ball.pos);
    double dist = phylib_length(subbed) - PHYLIB_BALL_DIAMETER;

    return dist;
  } else if (obj2->type == PHYLIB_ROLLING_BALL) {
    phylib_coord subbed = phylib_sub(pos1, obj2->obj.rolling_ball.pos);

    return (phylib_length(subbed) - PHYLIB_BALL_DIAMETER);
  } else if (obj2->type == PHYLIB_HOLE) {
    phylib_coord subbed = phylib_sub(pos1, obj2->obj.hole.pos);

    return (phylib_length(subbed) - PHYLIB_HOLE_RADIUS);
  } else if (obj2->type == PHYLIB_VCUSHION) {
    return fabs(pos1.x - obj2->obj.vcushion.x) - PHYLIB_BALL_RADIUS;
  } else if (obj2->type == PHYLIB_HCUSHION) {
    return fabs(pos1.y - obj2->obj.hcushion.y) - PHYLIB_BALL_RADIUS;
  }

  return -1;
}

/*
 *  Rolls a ball updates vel and pos
 */
void phylib_roll(phylib_object *new, phylib_object *old, double time) {
  if (new == NULL || old == NULL || new->type != PHYLIB_ROLLING_BALL ||
      old->type != PHYLIB_ROLLING_BALL) {
    return;
  }

  phylib_rolling_ball oldBall = old->obj.rolling_ball;

  new->obj.rolling_ball.pos.x = oldBall.pos.x + (oldBall.vel.x * time) +
                                ((oldBall.acc.x * time * time) / 2);
  new->obj.rolling_ball.pos.y = oldBall.pos.y + (oldBall.vel.y * time) +
                                ((oldBall.acc.y * time * time) / 2);

  new->obj.rolling_ball.vel.x = oldBall.vel.x + oldBall.acc.x *time;
  new->obj.rolling_ball.vel.y = oldBall.vel.y + oldBall.acc.y *time;

  if ((new->obj.rolling_ball.vel.x > 0 && old->obj.rolling_ball.vel.x < 0) ||
      (old->obj.rolling_ball.vel.x > 0 && new->obj.rolling_ball.vel.x < 0)) {
    new->obj.rolling_ball.vel.x = 0;
    new->obj.rolling_ball.acc.x = 0;
  }

  if ((new->obj.rolling_ball.vel.y > 0 && old->obj.rolling_ball.vel.y < 0) ||
      (old->obj.rolling_ball.vel.y > 0 && new->obj.rolling_ball.vel.y < 0)) {
    new->obj.rolling_ball.vel.y = 0;
    new->obj.rolling_ball.acc.y = 0;
  }
}

/*
 * Returns 1 if a rolling ball stops
 * Converts to a still ball
 */
unsigned char phylib_stopped(phylib_object *object) {
  if (object == NULL)
    return 0;

  if (object->type != PHYLIB_ROLLING_BALL)
    return 0;

  if (phylib_length(object->obj.rolling_ball.vel) < PHYLIB_VEL_EPSILON) {
    phylib_coord pos = object->obj.rolling_ball.pos;
    int number = object->obj.rolling_ball.number;
    object->type = PHYLIB_STILL_BALL;

    object->obj.still_ball.pos.x = pos.x;
    object->obj.still_ball.pos.y = pos.y;
    object->obj.still_ball.number = number;
    return 1;
  }

  return 0;
}

/*
 * A rolling ball bounces off another object
 * Reverses velocity
 */
void phylib_bounce(phylib_object **a, phylib_object **b) {
  if (a == NULL || (*a) == NULL || b == NULL || (*b) == NULL ||
      (*a)->type != PHYLIB_ROLLING_BALL) {
    return;
  }

  // printf("%d (num: %d) COLLIDED WITH %d\n", (*a)->type,
  //        (*a)->obj.rolling_ball.number, (*b)->type);

  switch ((*b)->type) {
    phylib_coord r_ab;
    phylib_coord v_rel;

  case PHYLIB_HCUSHION:
    (*a)->obj.rolling_ball.acc.y -= 2 * (*a)->obj.rolling_ball.acc.y;
    (*a)->obj.rolling_ball.vel.y -= 2 * (*a)->obj.rolling_ball.vel.y;
    break;

  case PHYLIB_VCUSHION:
    (*a)->obj.rolling_ball.acc.x -= 2 * (*a)->obj.rolling_ball.acc.x;
    (*a)->obj.rolling_ball.vel.x -= 2 * (*a)->obj.rolling_ball.vel.x;
    break;

  case PHYLIB_HOLE:
    if (*a != NULL) {
      free((*a));
      (*a) = NULL;
    }
    break;

  case PHYLIB_STILL_BALL:
    (*b)->type = PHYLIB_ROLLING_BALL;
    (*b)->obj.rolling_ball.vel.x = 0;
    (*b)->obj.rolling_ball.vel.y = 0;
    (*b)->obj.rolling_ball.acc.x = 0;
    (*b)->obj.rolling_ball.acc.y = 0;

  case PHYLIB_ROLLING_BALL:
    r_ab = phylib_sub((*a)->obj.rolling_ball.pos, (*b)->obj.rolling_ball.pos);
    v_rel = phylib_sub((*a)->obj.rolling_ball.vel, (*b)->obj.rolling_ball.vel);

    double length = phylib_length(r_ab);
    phylib_coord n;
    n.x = r_ab.x / length;
    n.y = r_ab.y / length;

    double v_rel_n = phylib_dot_product(v_rel, n);
    (*a)->obj.rolling_ball.vel.x -= (v_rel_n * n.x);
    (*a)->obj.rolling_ball.vel.y -= (v_rel_n * n.y);

    (*b)->obj.rolling_ball.vel.x += (v_rel_n * n.x);
    (*b)->obj.rolling_ball.vel.y += (v_rel_n * n.y);

    double speedA, speedB = 0;
    speedA = phylib_length((*a)->obj.rolling_ball.vel);
    speedB = phylib_length((*b)->obj.rolling_ball.vel);

    if (speedA > PHYLIB_VEL_EPSILON) {
      (*a)->obj.rolling_ball.acc.x =
          -(*a)->obj.rolling_ball.vel.x / speedA * PHYLIB_DRAG;
      (*a)->obj.rolling_ball.acc.y =
          -(*a)->obj.rolling_ball.vel.y / speedA * PHYLIB_DRAG;
    }

    if (speedB > PHYLIB_VEL_EPSILON) {
      (*b)->obj.rolling_ball.acc.x =
          -(*b)->obj.rolling_ball.vel.x / speedB * PHYLIB_DRAG;
      (*b)->obj.rolling_ball.acc.y =
          -(*b)->obj.rolling_ball.vel.y / speedB * PHYLIB_DRAG;
    }

    break;
  }
}

/*
 * Checks if a ball is rollin on the table
 * Returns number of rolling balls
 */
unsigned char phylib_rolling(phylib_table *t) {
  unsigned char num = 0;
  for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++) {
    if (t->object[i] == NULL)
      continue;

    if (t->object[i]->type == PHYLIB_ROLLING_BALL) {
      num++;
    }
  }

  return num;
}

/*
 * Returns a segment after a pool table
 * Loops through balls, rolling each until
 *   * Two balls collide
 *   * One ball stops
 *   * Max time is reached
 */
phylib_table *phylib_segment(phylib_table *table) {
  if (phylib_rolling(table) == 0) {
    return NULL;
  }
  phylib_table *newTable = phylib_copy_table(table);

  int looper = 1;

  phylib_object *hitObjects[PHYLIB_MAX_OBJECTS];
  for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++) {
    hitObjects[i] = NULL;
  }

  int hitCounter = 0;
  int counter = 1;
  while (looper) {

    for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++) {
        if (newTable->object[i] != NULL && newTable->object[i]->type == PHYLIB_ROLLING_BALL) {
            phylib_roll(newTable->object[i], table->object[i], counter * PHYLIB_SIM_RATE);
        }
    }

    for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++) {
        for (int j = 0; j < PHYLIB_MAX_OBJECTS; j++) {
            if (i == j)
                continue;

            double distance = phylib_distance(newTable->object[i], newTable->object[j]);

            if (distance == -1) {
                continue;
            }

            if (newTable->object[i] != NULL && newTable->object[j] != NULL &&
                distance < 0.0 &&
                newTable->object[i]->type == PHYLIB_ROLLING_BALL) {

            int alreadyCollided = 0;
            for (int k = 0; k < PHYLIB_MAX_OBJECTS; k++) {
                if (hitObjects[k] == newTable->object[j]) {
                    alreadyCollided = 1;
                    break;
                }
            }

            if (alreadyCollided == 0) {
                phylib_bounce(&newTable->object[i], &newTable->object[j]);
                hitObjects[hitCounter] = newTable->object[i];
                hitCounter++;
                looper = 0;
            }
        }
    }

    if (newTable->object[i] != NULL &&
        newTable->object[i]->type == PHYLIB_ROLLING_BALL &&
        phylib_stopped(newTable->object[i])) {
        looper = 0;
    }
    }

    if (PHYLIB_SIM_RATE * counter >= PHYLIB_MAX_TIME) {
        looper = 0;
    }

    counter++;
  }

  counter--;
  newTable->time += PHYLIB_SIM_RATE * counter;
  return newTable;
}

char *phylib_object_string(phylib_object *object) {
  static char string[80];
  if (object == NULL) {
    snprintf(string, 80, "NULL;");
    return string;
  }
  switch (object->type) {
  case PHYLIB_STILL_BALL:
    snprintf(string, 80, "STILL_BALL (%d,%6.1lf,%6.1lf)",
             object->obj.still_ball.number, object->obj.still_ball.pos.x,
             object->obj.still_ball.pos.y);
    break;
  case PHYLIB_ROLLING_BALL:
    snprintf(string, 80,
             "ROLLING_BALL (%d,%6.1lf,%6.1lf,%6.1lf,%6.1lf,%6.1lf,%6.1lf)",
             object->obj.rolling_ball.number, object->obj.rolling_ball.pos.x,
             object->obj.rolling_ball.pos.y, object->obj.rolling_ball.vel.x,
             object->obj.rolling_ball.vel.y, object->obj.rolling_ball.acc.x,
             object->obj.rolling_ball.acc.y);
    break;
  case PHYLIB_HOLE:
    snprintf(string, 80, "HOLE (%6.1lf,%6.1lf)", object->obj.hole.pos.x,
             object->obj.hole.pos.y);
    break;
  case PHYLIB_HCUSHION:
    snprintf(string, 80, "HCUSHION (%6.1lf)", object->obj.hcushion.y);
    break;
  case PHYLIB_VCUSHION:
    snprintf(string, 80, "VCUSHION (%6.1lf)", object->obj.vcushion.x);
    break;
  }
  return string;
}
