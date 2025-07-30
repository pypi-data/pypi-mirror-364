#if ! defined (BAS_BETA_H)
#   define BAS_BETA_H 1

#   include "bas_common.h"

BEGIN_C_DECLS

/*
 * texinfo: bas_beta_control
 * This data type permits to control the management of the @math{\beta}
 * bounds in the @code{bas_Denef_Lipshitz} function and, more precisely
 * in the @code{bas_Denef_Lipshitz_aux} subfunction.
 *
 * The value @code{bas_single_beta_control} corresponds to the strategy 
 * given in [Theorem 3.1, DL84]: the bound @math{\beta} is a single
 * nonnegative integer.
 *
 * The value @code{bas_vector_beta_control} is an optimization, leading
 * to lower bounds: the bound @math{\beta} is a vectior with one entry
 * per differential indeterminate for which formal power series are sought.
 */

enum bas_beta_control
{
  bas_single_beta_control,
  bas_vector_beta_control
};

/*
 * texinfo: bas_beta
 * This data type implements the beta bound in the @code{bas_Denef_Lipshitz_aux}
 * algorithm.
 *
 * The field @code{control} contains the type of control to be applied.
 *
 * The field @code{single} contains the value of @math{\beta} in the
 * @code{bas_single_beta_control} case.
 *
 * The field @code{vector} contains the value of @math{\beta} in the
 * @code{bas_vector_beta_control} case.
 *
 * In the documentation of functions, by @emph{entries of @math{\beta}}
 * we mean either the @code{single} field when @code{control}
 * contains @code{bas_single_beta_control}~; or the coordinates
 * of the @code{vector} table in the other case.
 */

struct bas_beta
{
  enum bas_beta_control control;
  ba0_int_p single;
  struct ba0_tableof_int_p vector;
};

struct bas_Yuple;

extern BAS_DLL void bas_init_beta (
    struct bas_beta *);

extern BAS_DLL struct bas_beta *bas_new_beta (
    void);

extern BAS_DLL void bas_set_Y_control_beta (
    struct bas_beta *,
    struct bav_tableof_symbol *,
    enum bas_beta_control);

extern BAS_DLL void bas_set_beta (
    struct bas_beta *,
    struct bas_beta *);

extern BAS_DLL void bas_set_int_beta (
    struct bas_beta *,
    ba0_int_p);

extern BAS_DLL void bas_max_componentwise_beta (
    struct bas_beta *,
    struct bas_beta *);

extern BAS_DLL void bas_max_componentwise2_beta (
    struct bas_beta *,
    struct ba0_tableof_int_p *);

extern BAS_DLL ba0_int_p bas_max_value_beta (
    struct bas_beta *);

extern BAS_DLL void bas_add_thetas_to_beta (
    struct bas_beta *,
    struct bas_Yuple *,
    struct bav_tableof_variable *,
    struct bav_tableof_term *);

extern BAS_DLL void bas_max_splitting_edge_beta (
    struct bas_beta *,
    struct bas_beta *,
    struct bad_splitting_edge *,
    struct bas_Yuple *);

extern BAS_DLL ba0_printf_function bas_printf_beta;

END_C_DECLS
#endif /* !BAS_BETA_H */
