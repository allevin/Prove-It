from proveit.basiclogic.boolean.theorems import trueInBool, falseInBool
from proveit.basiclogic import Forall, Exists, Not, Implies, Equals, And, TRUE, FALSE, inBool, BOOLEANS
from proveit.common import A, P, PofA
from proveit.basiclogic.common import PofTrue, PofFalse

# forall_{P} [(P(TRUE) = PofTrueVal) and (P(FALSE) = PofFalseVal)] => {[forall_{A in BOOLEANS} P(A)] = FALSE}, assuming PofTrueVal=FALSE or PofFalseVal=FALSE
def forallBoolEvalFalseDerivation(PofTrueVal, PofFalseVal):
    # hypothesis = [P(TRUE) = PofTrueVal] and [P(FALSE) in PofFalseVal]
    hypothesis = And(Equals(PofTrue, PofTrueVal), Equals(PofFalse, PofFalseVal))
    # P(TRUE) in BOOLEANS assuming hypothesis
    hypothesis.deriveLeft().inBoolViaBooleanEquality().prove({hypothesis})
    # P(FALSE) in BOOLEANS assuming hypothesis
    hypothesis.deriveRight().inBoolViaBooleanEquality().prove({hypothesis})
    # forall_{A in BOOLEANS} P(A) in BOOLEANS assuming hypothesis
    Forall(A, inBool(PofA), domain=BOOLEANS).concludeAsFolded().prove({hypothesis})
    if PofTrueVal == FALSE:
        # Not(P(TRUE)) assuming hypothesis
        hypothesis.deriveLeft().deriveViaBooleanEquality().prove({hypothesis})
        example = TRUE
        # TRUE in BOOLEANS
        trueInBool
    elif PofFalseVal == FALSE:
        # Not(P(FALSE)) assuming hypothesis
        hypothesis.deriveRight().deriveViaBooleanEquality().prove({hypothesis})
        example = FALSE    
        # FALSE in BOOLEANS
        falseInBool
    # [forall_{A in BOOLEANS} P(A)] = FALSE assuming hypothesis
    conclusion = Exists(A, Not(PofA), domain=BOOLEANS).concludeViaExample(example).deriveNegatedForall().equateNegatedToFalse().prove({hypothesis})
    # forall_{P} [(P(TRUE) = FALSE) and (P(FALSE) in BOOLEANS)] => {[forall_{A in BOOLEANS} P(A)] = FALSE}
    return Implies(hypothesis, conclusion).generalize(P)