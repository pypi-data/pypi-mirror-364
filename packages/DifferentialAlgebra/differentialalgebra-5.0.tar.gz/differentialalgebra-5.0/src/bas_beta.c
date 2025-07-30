#include "bas_beta.h"
#include "bas_Yuple.h"

/*
 * texinfo: bas_init_beta
 * Initialize @var{beta} with @code{bas_single_beta_control}.
 */

BAS_DLL void
bas_init_beta (
    struct bas_beta *beta)
{
  beta->control = bas_single_beta_control;
  beta->single = -1;
  ba0_init_table ((struct ba0_table *) &beta->vector);
}

/*
 * texinfo: bas_new_beta
 * Allocate a new @var{beta}, initialize it and return it.
 */

BAS_DLL struct bas_beta *
bas_new_beta (
    void)
{
  struct bas_beta *beta =
      (struct bas_beta *) ba0_alloc (sizeof (struct bas_beta));
  bas_init_beta (beta);
  return beta;
}

/*
 * texinfo: bas_set_beta
 * Assign @var{src} to @var{dst}.
 */

BAS_DLL void
bas_set_beta (
    struct bas_beta *dst,
    struct bas_beta *src)
{
  if (dst != src)
    {
      dst->control = src->control;
      dst->single = src->single;
      ba0_set_table ((struct ba0_table *) &dst->vector,
          (struct ba0_table *) &src->vector);
    }
}

/*
 * texinfo: bas_set_Y_control_beta
 * Reset @var{beta} using @var{Y} and @var{control}.
 * The argument @var{Y} is only useful in the @code{bas_vector_beta_control}
 * case.
 */

BAS_DLL void
bas_set_Y_control_beta (
    struct bas_beta *beta,
    struct bav_tableof_symbol *Y,
    enum bas_beta_control control)
{
  beta->control = control;
  beta->single = -1;
  if (control == bas_single_beta_control)
    ba0_reset_table ((struct ba0_table *) &beta->vector);
  else
    {
      ba0_int_p i;

      ba0_realloc_table ((struct ba0_table *) &beta->vector, Y->size);
      beta->vector.size = Y->size;
      for (i = 0; i < Y->size; i++)
        beta->vector.tab[i] = -1;
    }
}

/*
 * texinfo: bas_set_int_beta
 * Assign @var{value} to all entries of @var{beta}.
 */

BAS_DLL void
bas_set_int_beta (
    struct bas_beta *beta,
    ba0_int_p value)
{
  if (beta->control == bas_single_beta_control)
    beta->single = value;
  else
    {
      ba0_int_p i;

      for (i = 0; i < beta->vector.size; i++)
        beta->vector.tab[i] = value;
    }
}

/*
 * texinfo: bas_max_componentwise_beta
 * Assign to each entry of @var{max_beta} the maximum between
 * this value and the corresponding entry of @var{beta}.
 * Exception @code{BA0_ERRALG} is raised if the @code{control} field
 * of @var{max_beta} and @var{beta} are different.
 */

BAS_DLL void
bas_max_componentwise_beta (
    struct bas_beta *max_beta,
    struct bas_beta *beta)
{
  if (beta->control != max_beta->control)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  if (beta->control == bas_vector_beta_control &&
      beta->vector.size != max_beta->vector.size)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  if (beta->control == bas_single_beta_control)
    {
      if (beta->single > max_beta->single)
        max_beta->single = beta->single;
    }
  else
    {
      ba0_int_p i;
      for (i = 0; i < beta->vector.size; i++)
        {
          if (beta->vector.tab[i] > max_beta->vector.tab[i])
            max_beta->vector.tab[i] = beta->vector.tab[i];
        }
    }
}

/*
 * texinfo: bas_max_componentwise2_beta
 * Assign to @var{max_beta} the componentwise maximum vector 
 * of @var{max_beta} and @var{beta}. 
 * This function only applies in the @code{bas_vector_beta_control} case.
 * Exception @code{BA0_ERRALG} is raised in the
 * @code{bas_single_beta_control} case.
 */

BAS_DLL void
bas_max_componentwise2_beta (
    struct bas_beta *max_beta,
    struct ba0_tableof_int_p *beta)
{
  ba0_int_p i;

  if (max_beta->control != bas_vector_beta_control ||
      max_beta->vector.size != beta->size)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  for (i = 0; i < beta->size; i++)
    {
      if (beta->tab[i] > max_beta->vector.tab[i])
        max_beta->vector.tab[i] = beta->tab[i];
    }
}

/*
 * texinfo: bas_max_value_beta
 * Return the maximum of all the entries of @var{beta}.
 * This function only applies in the @code{bas_vector_beta_control} case.
 * Exception @code{BA0_ERRALG} is raised in the
 * @code{bas_single_beta_control} case.
 */

BAS_DLL ba0_int_p
bas_max_value_beta (
    struct bas_beta *beta)
{
  ba0_int_p i, max_value;

  if (beta->control == bas_single_beta_control || beta->vector.size == 0)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  max_value = beta->vector.tab[0];
  for (i = 1; i < beta->vector.size; i++)
    {
      if (beta->vector.tab[i] > max_value)
        max_value = beta->vector.tab[i];
    }
  return max_value;
}

/*
 * texinfo: bas_add_thetas_to_beta
 * In the @code{bas_vector_beta_control} case,
 * add the order of each derivative operator of @var{thetas} to the
 * corresponding entry of @var{beta}.
 * In the @code{beta_single_control} case,
 * add the maximum of these orders to the entry of @var{beta}.
 * In both cases, the entries which do not correspond to any element of the 
 * field @code{Y} of @var{U} are ignored.
 */

BAS_DLL void
bas_add_thetas_to_beta (
    struct bas_beta *beta,
    struct bas_Yuple *U,
    struct bav_tableof_variable *leaders,
    struct bav_tableof_term *thetas)
{
  struct bav_symbol *y;
  ba0_int_p i, j, k;

  if (beta->control == bas_single_beta_control)
    {
      if (thetas->size > 0)
        {
/*
 * Compute the max_order of entries of thetas which 
 * correspond to differential indeterminates in Y
 */
          ba0_int_p max_order = 0;
          for (i = 0; i < leaders->size; i++)
            {
              y = leaders->tab[i]->root;;
              j = bav_get_dictionary_symbol (&U->dict_Y, &U->Y, y);
              if (j != BA0_NOT_AN_INDEX)
                {
                  k = bav_total_degree_term (thetas->tab[i]);
                  if (k > max_order)
                    max_order = k;
                }
            }
          beta->single += max_order;
        }
    }
  else
    {
      for (i = 0; i < leaders->size; i++)
        {
          y = leaders->tab[i]->root;
          j = bav_get_dictionary_symbol (&U->dict_Y, &U->Y, y);
          if (j != BA0_NOT_AN_INDEX)
            {
              k = bav_total_degree_term (thetas->tab[i]);
              beta->vector.tab[j] += k;
            }
        }
    }
}


/*
 * texinfo: bas_max_splitting_edge_beta
 * In the @code{bas_vector_beta_control} case,
 * assign to the @var{s}th entry of @var{max_beta} the maximum
 * between this entry and the @var{d}th entries of @var{beta},
 * where @var{s} is the entry index associated to the source
 * symbol of @var{edge} and @var{d} runs over the entry indices associated
 * to all destination symbols.
 * If the source or the destination symbols of @var{edge} are not
 * associated to any entry of the vectors, the associated values
 * are supposed to be zero and the function does not perform anything.
 * In the @code{bas_single_beta_control} case, the function
 * does not perform anything.
 */

BAS_DLL void
bas_max_splitting_edge_beta (
    struct bas_beta *max_beta,
    struct bas_beta *beta,
    struct bad_splitting_edge *edge,
    struct bas_Yuple *U)
{
  if (!bad_has_var_typeof_splitting_edge (edge->type))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (beta->control != max_beta->control)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (max_beta->control == bas_vector_beta_control)
    {
      struct bav_symbol *src, *dst;
      ba0_int_p i, s, d;

      src = bad_src_symbol_splitting_edge (edge);
      s = bav_get_dictionary_symbol (&U->dict_Y, &U->Y, src);
      if (s != BA0_NOT_AN_INDEX)
        {
          for (i = 1; i < edge->leaders.size; i++)
            {
              dst = edge->leaders.tab[i]->root;
              d = bav_get_dictionary_symbol (&U->dict_Y, &U->Y, dst);
              if (d != BA0_NOT_AN_INDEX)
                {
                  if (beta->vector.tab[d] > max_beta->vector.tab[s])
                    max_beta->vector.tab[s] = beta->vector.tab[d];
                }
            }
        }
    }
}

/*
 * texinfo: bas_printf_beta
 * General printing function for @code{struct bas_beta}.
 * It can be called through @code{ba0_printf/%beta}.
 */

BAS_DLL void
bas_printf_beta (
    void *beta0)
{
  struct bas_beta *beta = (struct bas_beta *) beta0;

  if (beta->control == bas_single_beta_control)
    ba0_printf ("%d", beta->single);
  else
    ba0_printf ("%t[%d]", &beta->vector);
}
