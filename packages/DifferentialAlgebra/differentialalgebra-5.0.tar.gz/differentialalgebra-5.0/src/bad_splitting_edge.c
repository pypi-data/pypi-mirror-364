#include "bad_splitting_edge.h"

/*
 * texinfo: bad_init_splitting_edge
 * Initialize @var{E}.
 */

BAD_DLL void
bad_init_splitting_edge (
    struct bad_splitting_edge *E)
{
  E->type = bad_none_edge;
  E->src = BAD_NOT_A_NUMBER;
  E->dst = BAD_NOT_A_NUMBER;
  ba0_init_table ((struct ba0_table *) &E->leaders);
}

/*
 * texinfo: bad_new_splitting_edge
 * Allocate a new edge, initialize it and return it.
 */

BAD_DLL struct bad_splitting_edge *
bad_new_splitting_edge (
    void)
{
  struct bad_splitting_edge *E;

  E = (struct bad_splitting_edge *) ba0_alloc (sizeof (struct
          bad_splitting_edge));
  bad_init_splitting_edge (E);
  return E;
}

/*
 * texinfo: bad_set_splitting_edge
 * Assign @var{F} to @var{E}.
 */

BAD_DLL void
bad_set_splitting_edge (
    struct bad_splitting_edge *E,
    struct bad_splitting_edge *F)
{
  if (E != F)
    {
      E->type = F->type;
      E->src = F->src;
      E->dst = F->dst;
      ba0_set_table ((struct ba0_table *) &E->leaders,
          (struct ba0_table *) &F->leaders);
    }
}

/*
 * texinfo: bad_set_tsdl_splitting_edge
 * Assign @var{type}, @var{src}, @var{dst} and @var{leaders} 
 * to the corresponding fields of @var{E}. 
 * The @var{leaders} argument may be zero.
 * It is then considered to be the empty table.
 */

BAD_DLL void
bad_set_tsdl_splitting_edge (
    struct bad_splitting_edge *E,
    enum bad_typeof_splitting_edge type,
    ba0_int_p src,
    ba0_int_p dst,
    struct bav_tableof_variable *leaders)
{
  E->type = type;
  E->src = src;
  E->dst = dst;
  if (leaders == (struct bav_tableof_variable *) 0)
    ba0_reset_table ((struct ba0_table *) &E->leaders);
  else
    ba0_set_table ((struct ba0_table *) &E->leaders,
        (struct ba0_table *) leaders);
}

/*
 * texinfo: bad_set_tvsd_splitting_edge
 * Assign @var{type}, @var{src} and @var{dst} to the corresponding 
 * fields of @var{E}. Store @var{src_var} and @var{dst_var} in
 * the two first entries of the field @code{leaders} of @var{E}.
 */

BAD_DLL void
bad_set_tvsd_splitting_edge (
    struct bad_splitting_edge *E,
    enum bad_typeof_splitting_edge type,
    ba0_int_p src,
    struct bav_variable *src_var,
    ba0_int_p dst,
    struct bav_variable *dst_var)
{
  E->type = type;
  E->src = src;
  E->dst = dst;
  ba0_realloc_table ((struct ba0_table *) &E->leaders, 2);
  E->leaders.tab[0] = src_var;
  E->leaders.tab[1] = dst_var;
  E->leaders.size = 2;
}

/*
 * readonly data
 */

static struct
{
  enum bad_typeof_splitting_edge type;
  char *ident;
} bad_cases[] = { {bad_none_edge, "xxx"},
{bad_critical_pair_edge, "cri"},
{bad_critical_pair_novar_edge, "crik"},
{bad_redzero_edge, "rdz"},
{bad_zero_nonzero_first_edge, "frst"},
{bad_zero_nonzero_factor_edge, "fact"},
{bad_zero_nonzero_initial_edge, "ini"},
{bad_zero_nonzero_gcd_edge, "gcd"},
{bad_zero_nonzero_separant_edge, "sep"},
{bad_regularize_edge, "regu"},
{bad_reg_characteristic_edge, "regc"}
};

/*
 * texinfo: bad_typeof_splitting_edge_to_string
 * Return a string encoding for @var{type}.
 * The encoding is given by the following table
 * @verbatim
 * "xxx"  bad_none_edge
 * "cri"  bad_critical_pair_edge
 * "crik" bad_critical_pair_novar_edge
 * "rdz"  bad_redzero_edge
 * "frst" bad_zero_nonzero_first_edge
 * "fact" bad_zero_nonzero_factor_edge
 * "ini"  bad_zero_nonzero_initial_edge
 * "gcd"  bad_zero_nonzero_gcd_edge
 * "sep"  bad_zero_nonzero_separant_edge
 * "regu" bad_regularize_edge
 * "regc" bad_reg_characteristic_edge
 * @end verbatim
 */

BAD_DLL char *
bad_typeof_splitting_edge_to_string (
    enum bad_typeof_splitting_edge type)
{
  bool found = false;
  ba0_int_p n = (ba0_int_p) (sizeof (bad_cases) / sizeof (bad_cases[0]));
  ba0_int_p i = 0;

  while (i < n && !found)
    {
      if (type == bad_cases[i].type)
        found = true;
      else
        i += 1;
    }
  if (!found)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  return bad_cases[i].ident;
}

/*
 * texinfo: bad_has_var_typeof_splitting_edge
 * Return @code{true} if the @code{leaders} field should be nonempty
 * for an edge of type @var{type}.
 */

BAD_DLL bool
bad_has_var_typeof_splitting_edge (
    enum bad_typeof_splitting_edge type)
{
  enum bad_typeof_splitting_edge T[] =
      { bad_critical_pair_edge, bad_zero_nonzero_factor_edge,
    bad_zero_nonzero_initial_edge, bad_zero_nonzero_gcd_edge,
    bad_zero_nonzero_separant_edge
  };

  ba0_int_p i, n = (ba0_int_p) (sizeof (T) / sizeof (T[0]));
  bool found = false;

  for (i = 0; i < n && !found; i++)
    found = type == T[i];

  return found;
}

/*
 * texinfo: bad_zero_nonzero_typeof_splitting_edge
 * Return @code{true} if the edges of type @var{type}
 * are associated to splittings which generate inequations
 */

BAD_DLL bool
bad_zero_nonzero_typeof_splitting_edge (
    enum bad_typeof_splitting_edge type)
{
  enum bad_typeof_splitting_edge T[] =
      { bad_zero_nonzero_first_edge, bad_zero_nonzero_factor_edge,
    bad_zero_nonzero_initial_edge, bad_zero_nonzero_gcd_edge,
    bad_zero_nonzero_separant_edge
  };

  ba0_int_p i, n = (ba0_int_p) (sizeof (T) / sizeof (T[0]));
  bool found = false;

  for (i = 0; i < n && !found; i++)
    found = type == T[i];

  return found;
}

/*
 * texinfo: bad_src_symbol_splitting_edge
 * Return the symbol of the variable associated to the source vertex
 * of @var{E}.
 * Exception @code{BA0_ERRALG} is raised if the @code{leaders} field
 * of @var{E} is empty.
 */

BAD_DLL struct bav_symbol *
bad_src_symbol_splitting_edge (
    struct bad_splitting_edge *E)
{
  if (!bad_has_var_typeof_splitting_edge (E->type))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  return E->leaders.tab[0]->root;
}

/*
 * texinfo: bad_scanf_splitting_edge
 * The parsing function for splitting edges.
 * It is called by @code{ba0_scanf/%splitting_edge}.
 * The expected syntax is 
 * @code{<type, src, dst, [leader_1, ..., leader_n]}.
 */

BAD_DLL void *
bad_scanf_splitting_edge (
    void *A)
{
  struct bad_splitting_edge *E;
  enum bad_typeof_splitting_edge type = bad_none_edge;
  struct bav_tableof_variable leaders;
  ba0_int_p i, src, dst, n;
  char buffer[BA0_BUFSIZE];
  bool found;
  struct ba0_mark M;

  if (A == (void *) 0)
    E = bad_new_splitting_edge ();
  else
    E = (struct bad_splitting_edge *) A;

  ba0_push_another_stack ();
  ba0_record (&M);
  ba0_init_table ((struct ba0_table *) &leaders);
  ba0_scanf ("<%s, %d, %d, %t[%v]>", buffer, &src, &dst, &leaders);
  ba0_pull_stack ();

  found = false;
  i = 0;
  n = (ba0_int_p)(sizeof (bad_cases) / sizeof (bad_cases[0]));
  while (!found && i < n)
    {
      found = ba0_strcasecmp (buffer, bad_cases[i].ident) == 0;
      if (!found)
        i += 1;
    }
  if (found)
    type = bad_cases[i].type;
  else
    BA0_RAISE_PARSER_EXCEPTION (BA0_ERRSYN);

  if ((bad_has_var_typeof_splitting_edge (type) && leaders.size < 2) ||
      (!bad_has_var_typeof_splitting_edge (type) && leaders.size > 0))
    BA0_RAISE_PARSER_EXCEPTION (BA0_ERRSYN);

  bad_set_tsdl_splitting_edge (E, type, src, dst, &leaders);

  ba0_restore (&M);
  return E;
}

/*
 * texinfo: bad_printf_splitting_edge
 * The printing function for splitting edges.
 * It is called by @code{ba0_printf/%splitting_edge}.
 */

BAD_DLL void
bad_printf_splitting_edge (
    void *A)
{
  struct bad_splitting_edge *E = (struct bad_splitting_edge *) A;
  char *ident = bad_typeof_splitting_edge_to_string (E->type);

  ba0_printf ("<%s, %d, %d, %t[%v]>", ident, E->src, E->dst, &E->leaders);
}

static char _struct_splitting_edge[] = "struct bad_splitting_edge";

static char _struct_splitting_edge_leaders[] =
    "struct bad_splitting_edge.leaders";

BAD_DLL ba0_int_p
bad_garbage1_splitting_edge (
    void *A,
    enum ba0_garbage_code code)
{
  struct bad_splitting_edge *E = (struct bad_splitting_edge *) A;
  ba0_int_p n = 0;

  if (code == ba0_isolated)
    n += ba0_new_gc_info (E, sizeof (struct bad_splitting_edge),
        _struct_splitting_edge);
  if (E->leaders.tab != (struct bav_variable **) 0)
    n += ba0_new_gc_info
        (E->leaders.tab, sizeof (struct bav_variable *) * E->leaders.alloc,
        _struct_splitting_edge_leaders);
  return n;
}

BAD_DLL void *
bad_garbage2_splitting_edge (
    void *A,
    enum ba0_garbage_code code)
{
  struct bad_splitting_edge *E;

  if (code == ba0_isolated)
    E = (struct bad_splitting_edge *) ba0_new_addr_gc_info (A,
        _struct_splitting_edge);
  else
    E = (struct bad_splitting_edge *) A;

  if (E->leaders.tab != (struct bav_variable **) 0)
    E->leaders.tab =
        (struct bav_variable **) ba0_new_addr_gc_info (E->leaders.tab,
        _struct_splitting_edge_leaders);

  return E;
}

BAD_DLL void *
bad_copy_splitting_edge (
    void *A)
{
  struct bad_splitting_edge *E;

  E = bad_new_splitting_edge ();
  bad_set_splitting_edge (E, (struct bad_splitting_edge *) A);
  return E;
}
