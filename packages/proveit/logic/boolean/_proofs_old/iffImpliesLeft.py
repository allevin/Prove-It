from proveit.basiclogic import Implies, Iff
from proveit.common import A, B

Implies(Iff(A, B), Iff(A, B).definition().deriveRightViaEquivalence().deriveRight()).generalize((A, B)).qed(__file__)
