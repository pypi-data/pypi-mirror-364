#if !defined (BAD_ROSENFELD_GROEBNER_H)
#   define BAD_ROSENFELD_GROEBNER_H 1

#   include "bad_common.h"
#   include "bad_intersectof_regchain.h"
#   include "bad_base_field.h"
#   include "bad_splitting_control.h"
#   include "bad_splitting_tree.h"

BEGIN_C_DECLS

extern BAD_DLL void bad_Rosenfeld_Groebner (
    struct bad_intersectof_regchain *,
    struct bad_splitting_tree *,
    struct bap_tableof_polynom_mpz *,
    struct bap_tableof_polynom_mpz *,
    struct bad_base_field *,
    struct bad_regchain *,
    struct bad_splitting_control *);

extern BAD_DLL void bad_first_quadruple (
    struct bad_tableof_quadruple *,
    bool *,
    struct bad_splitting_tree *,
    struct bad_attchain *,
    struct bap_tableof_polynom_mpz *,
    struct bap_tableof_polynom_mpz *,
    enum bad_typeof_reduction,
    struct bad_base_field *,
    struct bad_regchain *);

extern BAD_DLL void bad_gcd_mod_quadruple (
    struct bap_tableof_polynom_mpz *,
    struct bad_tableof_quadruple *,
    struct bav_tableof_tableof_variable *,
    bool *,
    struct bad_splitting_tree *,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bav_variable *,
    struct bad_base_field *);

extern BAD_DLL void bad_split_on_separant_quadruple (
    struct bad_tableof_quadruple *,
    struct bav_tableof_variable *,
    struct bav_tableof_variable *,
    bool *,
    struct bad_splitting_tree *,
    struct bap_polynom_mpz *,
    struct bad_base_field *);

extern BAD_DLL void bad_split_on_initial_quadruple (
    struct bad_tableof_quadruple *,
    struct bav_tableof_variable *,
    struct bav_tableof_variable *,
    bool *,
    struct bad_splitting_tree *,
    struct bap_polynom_mpz *,
    struct bad_base_field *);

END_C_DECLS
#endif /* !BAD_ROSENFELD_GROEBNER_H */
