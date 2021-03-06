from proveit import Literal, Operation, USE_DEFAULTS, ProofFailure, InnerExpr
from proveit.logic.equality import SimplificationError
from proveit._common_ import j,k,l,m, n, A, B, C, D, E, F, G,  AA, BB, CC, DD, EE
from proveit.logic.boolean.booleans import inBool
from proveit.abstract_algebra.generic_methods import apply_commutation_thm, apply_association_thm, apply_disassociation_thm, groupCommutation, groupCommute

class And(Operation):
    # The operator of the And operation
    _operator_ = Literal(stringFormat='and', latexFormat=r'\land', context=__file__)
    
    def __init__(self, *operands):
        r'''
        And together any number of operands: :math:`A \land B \land C`
        '''
        Operation.__init__(self, And._operator_, operands)
    
    def conclude(self, assumptions):
        '''
        Try to automatically conclude this conjunction via composing the constituents.
        That is, conclude some :math:`A \land B \and ... \land Z` via
        :math:'A', :math:'B', ..., :math:'Z' individually.
        '''
        from ._theorems_ import trueAndTrue
        if self == trueAndTrue.expr: return trueAndTrue # simple special case
        return self.concludeViaComposition(assumptions)

    def concludeNegation(self, assumptions=USE_DEFAULTS):
        # Created by JML on 6/24/19
        from ._theorems_ import trueAndFalseNegated, falseAndTrueNegated, falseAndFalseNegated,andIfBoth, nandIfLeftButNotRight, nandIfRightButNotLeft
        from proveit.number import num
        if self in {trueAndFalseNegated.expr, falseAndTrueNegated.expr, falseAndFalseNegated.expr}:
            # should be disproven via one of the imported theorems as a simple special case
            return self.prove()
            # Prove that the conjunction is true by proving that one of its operands is false and then negate it.
        # In the first attempt, don't use automation to prove any of the operands so that
        # we don't waste time trying to prove operands when we already know one to be false
        for useAutomationForOperand in [False, True]:
            disprovenOperandIndices = []
            for k, operand in enumerate(self.operands):
                try:
                    operand.disprove(assumptions, automation=useAutomationForOperand)
                    disprovenOperandIndices.append(k)
                    self.concludeViaExample(operand, assumptions=assumptions)  # possible way to prove it
                except ProofFailure:
                    pass
            if len(self.operands) == 2 and len(disprovenOperandIndices) > 0:
                # One or both of the two operands were known to be true (without automation).
                # Try a possibly simpler proof than concludeViaExample.
                try:
                    if len(disprovenOperandIndices) == 2:
                        return self.andIfBoth(assumptions)
                    elif disprovenOperandIndices[0] == 0:
                        return nandIfLeftButNotRight.specialize({A: self.operands[0], B: self.operands[1]}, assumptions=assumptions)
                    else:
                        from ._theorems_ import nandIfNotLeft
                        return nandIfRightButNotLeft.specialize({A: self.operands[0], B: self.operands[1]}, assumptions=assumptions)
                except:
                    pass
            if len(disprovenOperandIndices) > 0:
                try:
                    # proven using concludeViaExample above (unless orIf[Any,Left,Right] was not a usable theorem,
                    # in which case this will fail and we can simply try the default below)
                    return self.prove(assumptions, automation=False)
                except:
                    # orIf[Any,Left,Right] must not have been a usable theorem; use the default below.
                    break


        '''
        If there is a negation, try to automatically conclude a few special cases.
        Then, evaluate each operand to prove the expression FALSE so the negation
        will be true.
        
        from ._theorems_ import trueAndFalseNegated, falseAndTrueNegated, falseAndFalseNegated
        from proveit.number import num
        from proveit.logic.boolean._common_ import TRUE, FALSE
        # Try a few special cases
        if len(self.operands) == 2:
            if self.operands == (TRUE, FALSE):
                return trueAndFalseNegated
            if self.operands == (FALSE, TRUE):
                return falseAndTrueNegated
            if self.operands == (FALSE, FALSE):
                return falseAndFalseNegated
        # Loop over the operands and see if there is an evaluation for the operands
        for idx,operand in enumerate(self.operands):
            try:
                evaluation = operand.evaluation(assumptions)
            except ProofFailure:
                continue
            if evaluation.rhs == FALSE:
                if len(self.operands) == 2:
                    if idx == 0:
                        # if the left side is false
                        try:
                            from ._theorems_ import nandIfNotLeft
                            return nandIfNotLeft.specialize({A: self.operands[0], B: self.operands[1]},assumptions=assumptions)
                        except ProofFailure:
                            continue
                    if idx == 1:
                        # if the right side is false
                        from ._theorems_ import nandIfNotRight
                        return nandIfNotRight.specialize({A: self.operands[0], B: self.operands[1]},assumptions=assumptions)
                else:
                    # if there is more than two operands, see if at least one of them is false. 
                    mVal, nVal = num(idx), num(len(self.operands) - idx - 1)
                    from ._theorems_ import nandIfNotOne
                    try:
                        return nandIfNotOne.specialize({m: mVal, n: nVal, AA: self.operands[:idx], B: self.operands[idx], CC: self.operands[idx + 1:]},assumptions=assumptions)
                    except ProofFailure:
                        continue
        '''
    def sideEffects(self, knownTruth):
        '''
        Side-effect derivations to attempt automatically.
        '''

        from proveit.logic import Not
        if len(self.operands) == 2:
            if self.operands[1] == Not(self.operands[0]):
                # (A or not(A)) is an unfolded Boolean
                return  # stop to avoid infinite recursion.
        yield self.deriveInBool
        yield self.deriveParts
        #yield self.deriveCommutation

    def negationSideEffects(self, knownTruth):
        '''
        Side-effect derivations to attempt automatically for Not(A and B and .. and .. Z).
        '''
        from proveit.logic import Not, Or
        yield self.deriveInBool # (A and B and ... and Z) in Booleans
        # implemented by JML on 7/2/19
        # If all of the operands are negated call the disjunction form of DeMorgan's
        if all(isinstance(operand, Not) for operand in self.operands):
            demorganOr = Or(*[operand.operand for operand in self.operands])
            yield demorganOr.concludeViaDemorgans
        
    def inBoolSideEffects(self, knownTruth):
        '''
        From (A and B and .. and Z) in Booleans deduce (A in Booleans), (B in Booleans), ...
        (Z in Booleans).
        '''
        yield self.deducePartsInBool
    
    def deriveInBool(self, assumptions=USE_DEFAULTS):
        '''
        From (A and B and ... and Z) derive [(A and B and ... and Z) in Booleans].
        '''
        return inBool(self).prove(assumptions=assumptions)
    
    def deriveParts(self, assumptions=USE_DEFAULTS):
        r'''
        From (A and B and ... and Z)` derive each operand:
        A, B, ..., Z.
        '''
        for i in range(len(self.operands)):
            self.deriveInPart(i, assumptions)

    def deriveInPart(self, indexOrExpr, assumptions=USE_DEFAULTS):
        r'''
        From (A and ... and X and ... and Z)` derive X.  indexOrExpr specifies 
        :math:`X` either by index or the expr.
        edited by JML 7/9/19 implement someFromAnd for side effect use
        '''
        from ._theorems_ import anyFromAnd, leftFromAnd, rightFromAnd, someFromAnd
        idx = indexOrExpr if isinstance(indexOrExpr, int) else list(self.operands).index(indexOrExpr)
        if idx < 0 or idx >= len(self.operands):
            raise IndexError("Operand out of range: " + str(idx))
        if len(self.operands)==2:
            if idx==0:
                return leftFromAnd.specialize({A:self.operands[0], B:self.operands[1]}, assumptions=assumptions)
            elif idx==1:
                return rightFromAnd.specialize({A:self.operands[0], B:self.operands[1]}, assumptions=assumptions)
        else:
            pass # Need to grab Joaquin's ExprTuple len method
            '''
            from proveit import ExprTuple
            from proveit.number import num
            try:
                mVal, nVal = num(idx), num(len(self.operands)-idx-1)
                print(mVal,nVal)
                mVal, nVal = ExprTuple(*self.operands[:idx]).len(), ExprTuple(*self.operands[idx + 1:]).len()
                print(mVal, nVal)
                return anyFromAnd.specialize({m:mVal, n:nVal, AA:self.operands[:idx], B:self.operands[idx], CC:self.operands[idx+1:]}, assumptions=assumptions)
            except ProofFailure:
                self.deriveSomeFromAnd(idx, assumptions)
            '''
    def deriveSomeFromAnd(self, idx, assumptions=USE_DEFAULTS):
        '''
        added by JML 7/8/19
        From (A and ... and B and ... C) derive any one index even if it is an iteration. 
        '''
        from proveit import ExprTuple
        from proveit.logic.boolean.conjunction._theorems_ import someFromAnd
        lVal = ExprTuple(*self.operands[:idx]).len()
        mVal = ExprTuple(self.operands[idx]).len()
        nVal = ExprTuple(*self.operands[idx + 1:]).len()
        return someFromAnd.specialize({l: lVal, m: mVal, n: nVal, AA:self.operands[:idx], BB:self.operands[idx], CC:self.operands[idx + 1:]}, assumptions = assumptions)

    def deriveLeft(self, assumptions=USE_DEFAULTS):
        r'''
        From :math:`(A \land B)` derive :math:`A`.
        '''
        if len(self.operands) != 2:
            raise Exception('deriveLeft only applicable for binary conjunction operations')
        return self.deriveInPart(0, assumptions)

    def deriveRight(self, assumptions=USE_DEFAULTS):
        r'''
        From :math:`(A \land B)` derive :math:`B`.
        '''
        if len(self.operands) != 2:
            raise Exception('deriveRight only applicable for binary conjunction operations')
        return self.deriveInPart(1, assumptions)

    def concludeViaComposition(self, assumptions=USE_DEFAULTS):
        '''
        Prove and return some (A and B ... and ... Z) via A, B, ..., Z each proven individually.
        See also the compose method to do this constructively.
        '''
        return compose(self.operands, assumptions)
    
    def deduceLeftInBool(self, assumptions=USE_DEFAULTS):
        '''
        Deduce A in Booleans from (A and B) in Booleans.
        '''
        from ._axioms_ import leftInBool
        if len(self.operands) == 2:
            leftInBool.specialize({A:self.operands[0], B:self.operands[1]}, assumptions=assumptions)
        
    def deduceRightInBool(self, assumptions=USE_DEFAULTS):
        '''
        Deduce B in Booleans from (A and B) in Booleans.
        '''
        from ._axioms_ import rightInBool
        if len(self.operands) == 2:
            rightInBool.specialize({A:self.operands[0], B:self.operands[1]}, assumptions=assumptions)

    def deducePartsInBool(self, assumptions=USE_DEFAULTS):
        '''
        Deduce A in Booleans, B in Booleans, ..., Z in Booleans
        from (A and B and ... and Z) in Booleans.
        '''
        for i in range(len(self.operands)):
            self.deducePartInBool(i, assumptions)        

    def deducePartInBool(self, indexOrExpr, assumptions=USE_DEFAULTS):
        '''
        Deduce X in Booleans from (A and B and .. and X and .. and Z) in Booleans
        provided X by expression or index number.
        '''
        from ._theorems_ import eachInBool
        idx = indexOrExpr if isinstance(indexOrExpr, int) else list(self.operands).index(indexOrExpr)
        if idx < 0 or idx >= len(self.operands):
            raise IndexError("Operand out of range: " + str(idx))
        if len(self.operands)==2:
            if idx == 0:
                return self.deduceLeftInBool(assumptions)
            elif idx==1:
                return self.deduceRightInBool(assumptions)
        else:
            from proveit.number import num
            mVal, nVal = num(idx), num(len(self.operands)-idx-1)
            return eachInBool.specialize({m:mVal, n:nVal, AA:self.operands[:idx], B:self.operands[idx], CC:self.operands[idx+1:]}, assumptions=assumptions)

    def concludeViaDemorgans(self, assumptions=USE_DEFAULTS):
        '''
        # created by JML 6/28/19
        From A and B and C conclude Not(Not(A) or Not(B) or Not(C))
        '''
        from ._theorems_ import demorgansLawOrToAnd, demorgansLawOrToAndBin
        from proveit.number import num
        if len(self.operands) == 2:
            return demorgansLawOrToAndBin.specialize({A:self.operands[0], B:self.operands[1]}, assumptions=assumptions)
        else:
            return demorgansLawOrToAnd.specialize({m:num(len(self.operands)), AA:self.operands}, assumptions=assumptions)

    def concludeViaExample(self, trueOperand, assumptions=USE_DEFAULTS):
        '''
        From one true operand, conclude that this 'or' expression is true.
        Requires all of the operands to be in the set of BOOLEANS.
        '''
        from proveit.number import num
        from ._theorems_ import nandIfNotOne, nandIfNotLeft, nandIfNotRight
        index = self.operands.index(trueOperand)
        if len(self.operands) == 2:
            if index == 0:
                return nandIfNotLeft.specialize({A:self.operands[0], B:self.operands[1]}, assumptions=assumptions)
            elif index == 1:
                return nandIfNotRight.specialize({A:self.operands[0], B:self.operands[1]}, assumptions=assumptions)
        return nandIfNotOne.specialize({m:num(index), n:num(len(self.operands)-index-1), AA:self.operands[:index], B:self.operands[index], CC:self.operands[index+1:]}, assumptions=assumptions)

    def evaluation(self, assumptions=USE_DEFAULTS):
        '''
        Given operands that evaluate to TRUE or FALSE, derive and
        return the equality of this expression with TRUE or FALSE. 
        '''
        from ._axioms_ import andTT, andTF, andFT, andFF # load in truth-table evaluations
        try:
            self.prove(assumptions)
        except ProofFailure:
            try:
                self.disprove(assumptions)
            except ProofFailure:
                pass
        return Operation.evaluation(self, assumptions)
    
    def deduceInBool(self, assumptions=USE_DEFAULTS):
        '''
        Attempt to deduce, then return, that this 'and' expression is in the set of BOOLEANS.
        '''
        
        from ._theorems_ import binaryClosure, closure
        if len(self.operands)==2:
            return binaryClosure.specialize({A:self.operands[0], B:self.operands[1]}, assumptions=assumptions)
        else:
            from proveit.number import num    
        return closure.specialize({m:num(len(self.operands)), AA:self.operands}, assumptions=assumptions)

    def commutation(self, initIdx=None, finalIdx=None, assumptions=USE_DEFAULTS):
        '''
        Given Boolean operands, deduce that this expression is equal to a form in which the operand
        at index initIdx has been moved to finalIdx.
        For example, (A and B and ... and Y and Z) = (A and ... and Y and B and Z)
        via initIdx = 1 and finalIdx = -2.
        '''
        from ._theorems_ import commutation, leftwardCommutation, rightwardCommutation
        return apply_commutation_thm(self, initIdx, finalIdx, commutation, leftwardCommutation, rightwardCommutation, assumptions)

    def groupCommutation(self, initIdx, finalIdx, length, disassociate=True, assumptions=USE_DEFAULTS):
        '''
        Given Boolean operands, deduce that this expression is equal to a form in which the operands
        at indices [initIdx, initIdx+length) have been moved to [finalIdx. finalIdx+length).
        It will do this by performing association first.  If disassocate is True, it
        will be disassociated afterwards.
        '''
        return groupCommutation(self, initIdx, finalIdx, length, disassociate, assumptions)
    
    def commute(self, initIdx=None, finalIdx=None, assumptions=USE_DEFAULTS):
        '''
        From self, derive and return a form in which the operand
        at index initIdx has been moved to finalIdx.
        For example, given (A and B and ... and Y and Z) derive (A and ... and Y and B and Z)
        via initIdx = 1 and finalIdx = -2.
        '''
        from ._theorems_ import commute, leftwardCommute, rightwardCommute      
        return apply_commutation_thm(self, initIdx, finalIdx, commute, leftwardCommute, rightwardCommute, assumptions)  
    
    def groupCommute(self, initIdx, finalIdx, length, disassociate=True, assumptions=USE_DEFAULTS):
        '''
        Given self, deduce and return a form in which the operands
        at indices [initIdx, initIdx+length) have been moved to [finalIdx. finalIdx+length).
        It will do this by performing association first.  If disassocate is True, it
        will be disassociated afterwards.
        '''
        return groupCommute(self, initIdx, finalIdx, length, disassociate, assumptions)
    
    def association(self, startIdx, length, assumptions=USE_DEFAULTS):
        '''
        Given Boolean operands, deduce that this expression is equal to a form in which operands in the
        range [startIdx, startIdx+length) are grouped together.
        For example, (A and B and ... and Y and Z) = (A and B ... and (L and ... and M) and ... and Y and Z)
        '''
        from ._theorems_ import association
        return apply_association_thm(self, startIdx, length, association, assumptions)

    def associate(self, startIdx, length, assumptions=USE_DEFAULTS):
        '''
        From self, derive and return a form in which operands in the
        range [startIdx, startIdx+length) are grouped together.
        For example, from (A and B and ... and Y and Z) derive
        (A and B ... and (L and ... and M) and ... and Y and Z).
        '''
        from ._theorems_ import associate
        return apply_association_thm(self, startIdx, length, associate, assumptions)

    def disassociation(self, idx, assumptions=USE_DEFAULTS):
        '''
        Given Boolean operands, deduce that this expression is equal to a form in which the operand
        at index idx is no longer grouped together.
        For example, (A and B ... and (L and ... and M) and ... and Y and Z) = (A and B and ... and Y and Z)
        '''
        from ._theorems_ import disassociation
        return apply_disassociation_thm(self, idx, disassociation, assumptions)

    def disassociate(self, idx, assumptions=USE_DEFAULTS):
        '''
        From self, derive and return a form in which the operand
        at the given index is ungrouped.
        For example, from (A and B ... and (L and ... and M) and ... and Y and Z)
        derive (A and B and ... and Y and Z).
        '''
        from ._theorems_ import disassociate
        return apply_disassociation_thm(self, idx, disassociate, assumptions)

    
def compose(expressions, assumptions=USE_DEFAULTS):
    '''
    Returns [A and B and ...], the And operator applied to the collection of given arguments,
    derived from each separately.
    '''
    if len(expressions)==2:
        from ._theorems_ import andIfBoth
        return andIfBoth.specialize({A:expressions[0], B:expressions[1]}, assumptions=assumptions)
    else:
        from proveit.number import num
        from ._theorems_ import andIfAll
        return andIfAll.specialize({m:num(len(expressions)), AA:expressions}, assumptions=assumptions)

# Register these expression equivalence methods:
InnerExpr.register_equivalence_method(And, 'commutation', 'commuted', 'commute')
InnerExpr.register_equivalence_method(And, 'groupCommutation', 'groupCommuted', 'groupCommute')
InnerExpr.register_equivalence_method(And, 'association', 'associated', 'associate')
InnerExpr.register_equivalence_method(And, 'disassociation', 'disassociated', 'disassociate')
