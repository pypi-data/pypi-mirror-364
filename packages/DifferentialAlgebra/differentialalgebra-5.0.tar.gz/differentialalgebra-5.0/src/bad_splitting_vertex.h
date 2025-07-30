#if !defined (BAD_SPLITTING_VERTEX_H)
#   define BAD_SPLITTING_VERTEX_H 1

#   include "bad_splitting_edge.h"

BEGIN_C_DECLS

/*
 * texinfo: bad_typeof_consistency_vertex
 * This data type is a subtype of @code{bad_splitting_vertex}.
 * It determines the consistency information of one vertex
 * of a splitting tree.
 */

enum bad_typeof_consistency_vertex
{
// the vertex is inconsistent
  bad_inconsistent_vertex,
// the vertex is rejected (by a dimension argument, ...)
  bad_rejected_vertex,
// the consistency of the vertex is uncertain (at least when created)
  bad_uncertain_vertex,
// the vertex is consistent
  bad_consistent_vertex
};

/*
 * texinfo: bad_inconsistency_argument_vertex
 * This data type is a subtype of @code{bad_splitting_vertex}.
 * It provides the argument which permitted to determine the inconsistency
 * of a vertex.
 */

enum bad_inconsistency_argument_vertex
{
// does not apply
  bad_none_argument,
// the reg_characteristic algorithm has not produced any regular chain
  bad_reg_characteric_argument,
// the new equation is a nonzero base field element
  bad_nonzero_base_field_equation_argument,
// the complete algorithm has not produced any quadruple
  bad_complete_argument,
// the complete algorithm, applied over a gcd, has not produced any quadruple
  bad_gcd_complete_argument
};

/*
 * texinfo: bad_splitting_vertex
 * This data type is a subtype of @code{bad_splitting_tree}.
 * It permits to describe one vertex of the tree.
 * Each vertex corresponds to a quadruple / regular chain, which
 * is identified by its @emph{number}.
 *
 * The field @code{number} contains the number of the vertex.
 *
 * The field @code{is_first} indicates if the vertex is a @dfn{first}
 * vertex. First vertices play a special role in elimination methods
 * for they provide bounds which permit to discard quadruples
 * by means of a dimension argument.
 *
 * The field @code{consistency} provides the consistency information
 * for the vertex. The default value is @code{bad_uncertain_vertex}.
 *
 * The field @code{argument} is only meaningful if @code{consistency}
 * is equal to @code{bad_inconsistent_vertex}. The default value
 * is @code{bad_none_argument}.
 *
 * The field @code{edges} contains the table of the edges starting
 * from the vertex towards other vertices of the splitting tree.
 * This table is sorted by increasing @code{dst} number.
 *
 * The fields @code{thetas} and @code{leaders} are only meaningful
 * if the successors of the vertex in the splitting tree were
 * obtained by a process invlving a differential reduction step.
 * In such a case, @code{leaders} contains the leaders of the
 * regular differential chain used to performed the reduction while
 * @code{thetas} contains the least common multiple of the derivative
 * operators applied to these regular differential chain elements
 * by the reduction. Both tables have the same size and there is a
 * one-to-one correspondence between there elements.
 *
 * The field @code{discarded_branch} indicates if a possible branch,
 * starting from the vertex, was discarded because of the presence
 * of differential inequations.
 */

struct bad_splitting_vertex
{
// the number of the vertex which is also the number of the quadruple
  ba0_int_p number;
// indicate if the vertex is a ``first'' vertex
  bool is_first;
// the consistency information for the vertex
  enum bad_typeof_consistency_vertex consistency;
// the argument which permitted to conclude that the vertex is inconsistent
  enum bad_inconsistency_argument_vertex argument;
// the edges towards the children of the vertex
  struct bad_tableof_splitting_edge edges;
// the derivative operators involved in a reduction process (if applicable)
  struct bav_tableof_term thetas;
// the leaders of the polynomials they have applied to (if applicable)
  struct bav_tableof_variable leaders;
// does there exist a discarded branch starting from the vertex?
  bool discarded_branch;
};

struct bad_tableof_splitting_vertex
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct bad_splitting_vertex **tab;
};

extern BAD_DLL void bad_init_splitting_vertex (
    struct bad_splitting_vertex *);

extern BAD_DLL struct bad_splitting_vertex *bad_new_splitting_vertex (
    void);

extern BAD_DLL void bad_reset_splitting_vertex (
    struct bad_splitting_vertex *,
    ba0_int_p);

extern BAD_DLL void bad_set_splitting_vertex (
    struct bad_splitting_vertex *,
    struct bad_splitting_vertex *);

extern BAD_DLL void bad_merge_thetas_leaders_splitting_vertex (
    struct bad_splitting_vertex *,
    struct bav_tableof_term *,
    struct bav_tableof_variable *);

extern BAD_DLL void bad_set_discarded_branch_splitting_vertex (
    struct bad_splitting_vertex *,
    bool);

extern BAD_DLL ba0_scanf_function bad_scanf_splitting_vertex;

extern BAD_DLL ba0_printf_function bad_printf_splitting_vertex;

extern BAD_DLL ba0_garbage1_function bad_garbage1_splitting_vertex;

extern BAD_DLL ba0_garbage2_function bad_garbage2_splitting_vertex;

extern BAD_DLL ba0_copy_function bad_copy_splitting_vertex;


END_C_DECLS
#endif /* !BAD_SPLITTING_VERTEX_H */
