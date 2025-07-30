#include "bad_splitting_tree.h"

/*
 * texinfo: bad_init_splitting_tree
 * Initialize @var{tree} to an empty inactive splitting tree.
 */

BAD_DLL void
bad_init_splitting_tree (
    struct bad_splitting_tree *tree)
{
  tree->activity = bad_inactive_splitting_tree;
  ba0_init_table ((struct ba0_table *) &tree->vertices);
  tree->number = 1;
}

/*
 * texinfo: bad_new_splitting_tree
 * Allocate a new splitting tree, initialize it and return it.
 */

BAD_DLL struct bad_splitting_tree *
bad_new_splitting_tree (
    void)
{
  struct bad_splitting_tree *tree;

  tree = (struct bad_splitting_tree *) ba0_alloc (sizeof (struct
          bad_splitting_tree));
  bad_init_splitting_tree (tree);
  return tree;
}

/*
 * texinfo: bad_reset_splitting_tree
 * Reset @var{tree} to an empty splitting tree with activity level @var{level}.
 */

BAD_DLL void
bad_reset_splitting_tree (
    struct bad_splitting_tree *tree,
    enum bad_activity_level_splitting_tree level)
{
  tree->activity = level;
  ba0_reset_table ((struct ba0_table *) &tree->vertices);
  tree->number = 1;
}

static void
bad_realloc_tableof_splitting_vertex (
    struct bad_tableof_splitting_vertex *T,
    ba0_int_p n)
{
  if (n > T->alloc)
    {
      ba0_int_p new_alloc = 2 * T->alloc + 1;
      while (new_alloc < n)
        new_alloc = 2 * new_alloc + 1;
      ba0_realloc2_table ((struct ba0_table *) T, new_alloc,
          (ba0_new_function *) & bad_new_splitting_vertex);
    }
}

static void
bad_set_tableof_splitting_vertex (
    struct bad_tableof_splitting_vertex *dst,
    struct bad_tableof_splitting_vertex *src)
{
  ba0_int_p i;

  if (dst != src)
    {
      ba0_realloc2_table ((struct ba0_table *) dst, src->size,
          (ba0_new_function *) & bad_new_splitting_vertex);
      for (i = 0; i < src->size; i++)
        bad_set_splitting_vertex (dst->tab[i], src->tab[i]);
      dst->size = src->size;
    }
}

/*
 * texinfo: bad_set_splitting_tree
 * Assign @var{src} to @var{dst}.
 */

BAD_DLL void
bad_set_splitting_tree (
    struct bad_splitting_tree *dst,
    struct bad_splitting_tree *src)
{
  if (dst != src)
    {
      dst->activity = src->activity;
      bad_set_tableof_splitting_vertex (&dst->vertices, &src->vertices);
      dst->number = src->number;
    }
}

/*
 * texinfo: bad_next_number_splitting_tree
 * Return the next available quadruple or regular chain number
 * available in @var{tree}. This function does not allocate any memory.
 */

BAD_DLL ba0_int_p
bad_next_number_splitting_tree (
    struct bad_splitting_tree *tree)
{
  return tree->number++;
}

/*
 * texinfo: bad_ith_vertex_splitting_tree
 * Return the splitting vertex dedicated to the quadruple or the regular
 * chain identified by @var{number} in @var{tree}.
 * This function may perform memory allocation.
 */

BAD_DLL struct bad_splitting_vertex *
bad_ith_vertex_splitting_tree (
    struct bad_splitting_tree *tree,
    ba0_int_p number)
{
  struct bad_splitting_vertex *V;
  ba0_int_p i = number;

  if (i < 0 || i >= tree->number)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (i >= tree->vertices.size)
    {
      bad_realloc_tableof_splitting_vertex (&tree->vertices, tree->number);
      while (i >= tree->vertices.size)
        {
          bad_reset_splitting_vertex (tree->vertices.tab[tree->vertices.size],
              tree->vertices.size);
          tree->vertices.size += 1;
        }
    }

  V = tree->vertices.tab[i];
  return V;
}

/*
 * texinfo: bad_set_first_vertex_splitting_tree
 * Set the @code{is_first} field of the vertex of @var{tree} with
 * number @var{number} to @var{is_first}. If @var{is_first} is
 * @code{true} then the vertex becomes a @emph{first} vertex.
 */

BAD_DLL void
bad_set_first_vertex_splitting_tree (
    struct bad_splitting_tree *tree,
    ba0_int_p number,
    bool is_first)
{
  struct bad_splitting_vertex *v = bad_ith_vertex_splitting_tree (tree, number);
  v->is_first = is_first;
}

/*
 * texinfo: bad_is_first_vertex_splitting_tree
 * Return @code{true} if @var{number} is the number of a @emph{first} vertex
 * else @code{false}.
 */

BAD_DLL bool
bad_is_first_vertex_splitting_tree (
    struct bad_splitting_tree *tree,
    ba0_int_p number)
{
  struct bad_splitting_vertex *V;

  if (number < 0 || number >= tree->number)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (number >= tree->vertices.size)
    return false;

  V = tree->vertices.tab[number];
  return V->is_first;
}

/*
 * texinfo: bad_add_edge_splitting_tree
 * Add the edge defined by the five last arguments to @var{tree}.
 * In the case of an inactive splitting tree, the edge is not recorded.
 * If an edge from @var{src} to @var{dst} has already been defined
 * then it must have the same type as @var{type} and the same
 * source variable as @var{src_var}. In such a case, @var{dst_var}
 * is added to the @code{leaders} field of the edge.
 * Exception @code{BA0_ERRALG} is raised if @var{src} and @var{dst}
 * are equal.
 */

BAD_DLL void
bad_add_edge_splitting_tree (
    struct bad_splitting_tree *tree,
    enum bad_typeof_splitting_edge type,
    ba0_int_p src,
    struct bav_variable *src_var,
    ba0_int_p dst,
    struct bav_variable *dst_var)
{
  struct bad_splitting_vertex *V;
  ba0_int_p i;
  bool found;

  if (src == BAD_NOT_A_NUMBER || src >= tree->number)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (dst == BAD_NOT_A_NUMBER || dst >= tree->number)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (src == dst)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (!bad_has_var_typeof_splitting_edge (type))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (tree->activity != bad_inactive_splitting_tree
      && dst_var != BAV_NOT_A_VARIABLE)
    {
/*
 * The next call is only meant to create the vertex dst
 */
      bad_ith_vertex_splitting_tree (tree, dst);

      V = bad_ith_vertex_splitting_tree (tree, src);
/*
 * Look for an existing edge between src and dst
 */
      i = 0;
      found = false;
      while (i < V->edges.size && !found)
        {
          if (V->edges.tab[i]->dst == dst)
            found = true;
          else
            i += 1;
        }
      if (found)
        {
          struct bad_splitting_edge *E = V->edges.tab[i];
/*
 * Add dst_var to E->leaders if not already present
 */
          if (E->type != type)
            BA0_RAISE_EXCEPTION (BA0_ERRALG);

          if (!ba0_member_table (dst_var, (struct ba0_table *) &E->leaders))
            {
              if (E->leaders.size == E->leaders.alloc)
                {
                  ba0_int_p new_alloc = 2 * E->leaders.alloc + 1;
                  ba0_realloc_table ((struct ba0_table *) &E->leaders,
                      new_alloc);
                }
              E->leaders.tab[E->leaders.size] = dst_var;
              E->leaders.size += 1;
            }
        }
      else
        {
/*
 * Add the new edge between src and dst
 */
          if (V->edges.size == V->edges.alloc)
            {
              ba0_int_p new_alloc = 2 * V->edges.alloc + 2;
              ba0_realloc2_table ((struct ba0_table *) &V->edges, new_alloc,
                  (ba0_new_function *) & bad_new_splitting_edge);
            }

          bad_set_tvsd_splitting_edge (V->edges.tab[V->edges.size],
              type, src, src_var, dst, dst_var);
          V->edges.size += 1;

          i = V->edges.size - 2;
          while (i >= 0 && V->edges.tab[i]->dst > dst)
            i -= 1;
          ba0_move_from_tail_table ((struct ba0_table *) &V->edges,
              (struct ba0_table *) &V->edges, i + 1);
        }
    }
}

/*
 * texinfo: bad_add_edge_novar_splitting_tree
 * Add the edge defined by @var{type}, @var{src} and @var{dst} to @var{tree}. 
 * In the case of an inactive splitting tree, the edge is not recorded.
 * Exception @code{BA0_ERRALG} is raised if @var{src} and @var{dst}
 * are equal.
 */

BAD_DLL void
bad_add_edge_novar_splitting_tree (
    struct bad_splitting_tree *tree,
    enum bad_typeof_splitting_edge type,
    ba0_int_p src,
    ba0_int_p dst)
{
  struct bad_splitting_vertex *V;
  ba0_int_p i;

  if (src == BAD_NOT_A_NUMBER || src >= tree->number)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (dst == BAD_NOT_A_NUMBER || dst >= tree->number)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (src == dst)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (bad_has_var_typeof_splitting_edge (type))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (tree->activity != bad_inactive_splitting_tree && src != dst)
    {
/*
 * The next call is only meant to create the vertex dst
 */
      bad_ith_vertex_splitting_tree (tree, dst);

      V = bad_ith_vertex_splitting_tree (tree, src);
/*
 * Check consistency of src and the fact that the edge is not
 *      already stored
 */
      for (i = 0; i < V->edges.size; i++)
        if (V->edges.tab[i]->src != src || V->edges.tab[i]->dst == dst)
          BA0_RAISE_EXCEPTION (BA0_ERRALG);

      if (V->edges.size == V->edges.alloc)
        {
          ba0_int_p new_alloc = 2 * V->edges.alloc + 2;
          ba0_realloc2_table ((struct ba0_table *) &V->edges, new_alloc,
              (ba0_new_function *) & bad_new_splitting_edge);
        }

      bad_set_tsdl_splitting_edge (V->edges.tab[V->edges.size],
          type, src, dst, (struct bav_tableof_variable *) 0);
      V->edges.size += 1;

      i = V->edges.size - 2;
      while (i >= 0 && V->edges.tab[i]->dst > dst)
        i -= 1;
      ba0_move_from_tail_table ((struct ba0_table *) &V->edges,
          (struct ba0_table *) &V->edges, i + 1);
    }
}

/*
 * texinfo: bad_set_vertex_consistency_splitting_tree
 * Set the fields @code{consistency} and @code{argument} of 
 * the vertex @var{number} of @var{tree}
 * to @var{consistency} and @var{argument}.
 * If @var{consistency} is different from @code{bad_inconsistent_vertex}
 * then the field @code{argument} is set to @code{bad_none_argument}.
 */

BAD_DLL void
bad_set_vertex_consistency_splitting_tree (
    struct bad_splitting_tree *tree,
    ba0_int_p number,
    enum bad_typeof_consistency_vertex consistency,
    enum bad_inconsistency_argument_vertex argument)
{
  struct bad_splitting_vertex *V;

  if (number < tree->vertices.size
      || tree->activity != bad_inactive_splitting_tree)
    {
      V = bad_ith_vertex_splitting_tree (tree, number);

      V->consistency = consistency;
      if (consistency != bad_inconsistent_vertex)
        V->argument = bad_none_argument;
      else
        V->argument = argument;
    }
}

/*
 * texinfo: bad_set_discarded_branch_splitting_tree
 * Assign @var{discarded_branch} to the corresponding field of the vertex
 * @var{number} of @var{tree}.
 * In the case of an inactive splitting tree, the edge is not recorded.
 */

BAD_DLL void
bad_set_discarded_branch_splitting_tree (
    struct bad_splitting_tree *tree,
    ba0_int_p number,
    bool discarded_branch)
{
  if (number < 0 || number >= tree->number)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (tree->activity != bad_inactive_splitting_tree)
    {
      struct bad_splitting_vertex *V;
      V = bad_ith_vertex_splitting_tree (tree, number);
/*
 * It may happen that V->discarded_branch is already set but
 * thetas and leaders should be the same as at the previous call
 */
      bad_set_discarded_branch_splitting_vertex (V, discarded_branch);
    }
}

/*
 * texinfo: bad_merge_thetas_leaders_vertex_splitting_tree
 * Let @var{V} denote the vertex of @var{tree} with number @var{number}.
 * Merge the field @code{leaders} of @var{V} with
 * @var{leaders} so that the resulting field @code{leaders}
 * of @var{V} remains sorted by decreasing order.
 * Perform corresponding operations on the field @code{thetas}
 * of @var{V} and @var{thetas}.
 * In the case of a same entry in the field @code{leaders}
 * of @var{V} and @var{leaders}, the least common multiple
 * of the corresponding entries of the field @code{thetas}
 * of @var{V} and @var{thetas} is taken.
 * The table @var{leaders} is supposed to be sorted by decreasing
 * order.
 */

BAD_DLL void
bad_merge_thetas_leaders_vertex_splitting_tree (
    struct bad_splitting_tree *tree,
    ba0_int_p number,
    struct bav_tableof_term *thetas,
    struct bav_tableof_variable *leaders)
{
  if (number < 0 || number >= tree->number)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (tree->activity != bad_inactive_splitting_tree)
    {
      struct bad_splitting_vertex *V;
      V = bad_ith_vertex_splitting_tree (tree, number);
      bad_merge_thetas_leaders_splitting_vertex (V, thetas, leaders);
    }
}

/*
 * dot splitting tree
 */

/*
 * Print the thetas/leaders information
 */

static void
bad_dot_thetas_leaders_splitting_tree (
    char *buffer,
    ba0_int_p n,
    struct bav_tableof_term *thetas,
    struct bav_tableof_variable *leaders)
{
  ba0_int_p i;
  bool yet;
  char buffaux[BA0_BUFSIZE];

  ba0_sprintf (buffer, "\"%d ", n);
  yet = false;
  for (i = 0; i < leaders->size; i++)
    {
      if (yet)
        ba0_sprintf (buffaux, ",%v:%term", leaders->tab[i], thetas->tab[i]);
      else
        ba0_sprintf (buffaux, "%v:%term", leaders->tab[i], thetas->tab[i]);
      strcat (buffer, buffaux);
      yet = true;
    }
  strcat (buffer, "\"");
}

/*
 * Print the content of vertex v
 */

static void
bad_dot_vertex_splitting_tree (
    char *buffer,
    struct bad_splitting_vertex *v)
{
  ba0_int_p n = v->number;
  if (v->thetas.size == 0)
    ba0_sprintf (buffer, "%d", n);
  else
    bad_dot_thetas_leaders_splitting_tree (buffer, n, &v->thetas, &v->leaders);
}

/*
 * Print the subtree starting at vertex number n
 */

static void
bad_dot_aux_splitting_tree (
    struct bad_splitting_tree *tree,
    ba0_int_p n)
{
  struct bad_splitting_vertex *v = tree->vertices.tab[n];
  char src[BA0_BUFSIZE];
  ba0_int_p i;
/*
 * Get the content of the vertex
 */
  bad_dot_vertex_splitting_tree (src, v);
/*
 * Print it with the adapted shape
 */
  switch (v->consistency)
    {
    case bad_rejected_vertex:
      ba0_printf ("  %s [shape=parallelogram];\n", src);
      break;
    case bad_uncertain_vertex:
      {
        bool only_box_children = true;
        for (i = 0; i < v->edges.size && only_box_children; i++)
          {
            struct bad_splitting_vertex *w;
            w = tree->vertices.tab[v->edges.tab[i]->dst];
            only_box_children = w->consistency == bad_consistent_vertex;
          }
        if (only_box_children)
          ba0_printf ("  %s [shape=hexagon];\n", src);
      }
      break;
    case bad_consistent_vertex:
      ba0_printf ("  %s [shape=box];\n", src);
      break;
    case bad_inconsistent_vertex:
      switch (v->argument)
        {
        case bad_none_argument:
          BA0_RAISE_EXCEPTION (BA0_ERRALG);
          break;
        case bad_reg_characteric_argument:
          ba0_printf ("  %s [shape=hexagon];\n", src);
          break;
        case bad_nonzero_base_field_equation_argument:
          ba0_printf ("  %s [shape=pentagon];\n", src);
          break;
        case bad_complete_argument:
          ba0_printf ("  %s [shape=septagon];\n", src);
          break;
        case bad_gcd_complete_argument:
          ba0_printf ("  %s [shape=octagon];\n", src);
          break;
        }
      break;
    }
/*
 * Print a fake edge if v has a discarded branch
 */
  if (v->discarded_branch)
    {
      char dst[BA0_BUFSIZE];
      ba0_sprintf (dst, "\" %d\"", v->number);
      ba0_printf ("  %s [shape=triangle];\n", dst);
      ba0_printf ("  %s -\\> %s;\n", src, dst);
    }
/*
 * Print all edges starting from v
 */
  for (i = 0; i < v->edges.size; i++)
    {
      char dst[BA0_BUFSIZE], lab[BA0_BUFSIZE];
      struct bad_splitting_vertex *w = tree->vertices.tab[v->edges.tab[i]->dst];
      char *ident;

      ident = bad_typeof_splitting_edge_to_string (v->edges.tab[i]->type);
      if (bad_has_var_typeof_splitting_edge (v->edges.tab[i]->type))
        {
          struct bad_splitting_edge *E = v->edges.tab[i];
          struct bav_tableof_variable T;
          struct ba0_mark M;
          ba0_record (&M);
          ba0_init_table ((struct ba0_table *) &T);
          ba0_set_table ((struct ba0_table *) &T, (struct ba0_table *)
              &E->leaders);
          ba0_delete_table ((struct ba0_table *) &T, 0);
          ba0_sprintf (lab, "\"%s/%v:%t[%v]\"", ident, E->leaders.tab[0], &T);
          ba0_restore (&M);
        }
      else
        ba0_sprintf (lab, "%s", ident);

      bad_dot_vertex_splitting_tree (dst, w);

      if (v->edges.tab[i]->type == bad_none_edge)
        ba0_printf ("  %s -\\> %s;\n", src, dst);
      else
        ba0_printf ("  %s -\\> %s [label=%s];\n", src, dst, lab);
    }
/*
 * Process recursively all targets of all edges
 */
  for (i = 0; i < v->edges.size; i++)
    {
      ba0_int_p m = v->edges.tab[i]->dst;
      bad_dot_aux_splitting_tree (tree, m);
    }
}

/*
 * texinfo: bad_dot_splitting_tree
 * Print @var{tree} as a directed graph, following the syntax 
 * of @code{graphviz/dot}. 
 * Edges are labelled using the encoding given by 
 * @code{bad_typeof_splitting_edge_to_string}.
 * The shapes of the vertices are functions of their
 * fields @code{consistency} and @code{argument}.
 * The correspondence is as follows:
 * @verbatim
 * ellipse       bad_uncertain_vertex (intermediate vertex)
 * parallelogram bad_rejected_vertex (dimension argument, ...)
 * box           bad_consistent_vertex (output regular differential chain)
 * hexagon       processed by reg_characteristic
 * pentagon      bad_inconsistent_vertex + 
 *                             bad_nonzero_base_field_equation_argument
 * septagon      bad_inconsistent_vertex + bad_complete_argument
 * octagon       bad_inconsistent_vertex + bad_gcd_complete_argument
 * @end verbatim
 * Discarded branches are displayed as @code{triangle} shape nodes.
 */


BAD_DLL void
bad_dot_splitting_tree (
    struct bad_splitting_tree *tree)
{
  if (tree->activity == bad_inactive_splitting_tree)
    return;

  ba0_printf ("digraph G \\{\n");
  bad_dot_aux_splitting_tree (tree, 0);
  ba0_printf ("\\}\n");
}

/*
 * texinfo: bad_scanf_splitting_tree
 * The parsing function for splitting trees.
 * It is called by @code{ba0_scanf/%splitting_tree}.
 * The read splitting tree is verbose.
 */

BAD_DLL void *
bad_scanf_splitting_tree (
    void *A)
{
  struct bad_splitting_tree *tree;
  ba0_int_p i;

  if (A == (void *) 0)
    tree = bad_new_splitting_tree ();
  else
    tree = (struct bad_splitting_tree *) A;

  ba0_scanf ("%t[%splitting_vertex]", &tree->vertices);

  tree->activity = bad_verbose_splitting_tree;

  for (i = 0; i < tree->vertices.size; i++)
    if (tree->vertices.tab[i]->number != i)
      BA0_RAISE_EXCEPTION (BA0_ERRALG);

  tree->number = tree->vertices.size;

  return tree;
}

/*
 * texinfo: bad_printf_splitting_tree
 * The printing function for splitting trees.
 * It is called by @code{ba0_printf/%splitting_tree}.
 */

BAD_DLL void
bad_printf_splitting_tree (
    void *A)
{
  struct bad_splitting_tree *tree = (struct bad_splitting_tree *) A;

  if (tree->activity != bad_inactive_splitting_tree)
    ba0_printf ("%t[%splitting_vertex]", &tree->vertices);
  else
    ba0_printf ("inactive splitting tree");
}

static char _struct_splitting_tree[] = "struct bad_splitting_tree";

BAD_DLL ba0_int_p
bad_garbage1_splitting_tree (
    void *A,
    enum ba0_garbage_code code)
{
  struct bad_splitting_tree *tree = (struct bad_splitting_tree *) A;
  ba0_int_p n = 0;

  if (code == ba0_isolated)
    n += ba0_new_gc_info (tree, sizeof (struct bad_splitting_tree),
        _struct_splitting_tree);
  n += ba0_garbage1 ("%t[%splitting_vertex]", &tree->vertices, ba0_embedded);
  return n;
}

BAD_DLL void *
bad_garbage2_splitting_tree (
    void *A,
    enum ba0_garbage_code code)
{
  struct bad_splitting_tree *tree;

  if (code == ba0_isolated)
    tree = (struct bad_splitting_tree *) ba0_new_addr_gc_info (A,
        _struct_splitting_tree);
  else
    tree = (struct bad_splitting_tree *) A;
  ba0_garbage2 ("%t[%splitting_vertex]", &tree->vertices, ba0_embedded);
  return tree;
}

BAD_DLL void *
bad_copy_splitting_tree (
    void *A)
{
  struct bad_splitting_tree *tree;

  tree = bad_new_splitting_tree ();
  bad_set_splitting_tree (tree, (struct bad_splitting_tree *) A);
  return tree;
}
