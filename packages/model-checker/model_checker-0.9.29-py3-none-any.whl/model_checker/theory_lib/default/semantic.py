"""This module implements the core semantic framework for generating Z3 constraints
to be added to a Z3 solver, finding Z3 models, and using those models to construct
semantic models over which the sentences of the language may be evaluated and printed.
This module does not include semantic clauses for the operators included in the
language since this is covered by a dedicated module.

The module provides three main classes that together form the semantic foundation:

1. Semantics: Implements the semantic framework for modal logic, including:
   - State-based verification and falsification conditions
   - Compatibility and fusion relations between states
   - Truth conditions for complex formulas
   - Alternative world calculations for counterfactuals
   - Extended verification/falsification relations

2. Proposition: Represents propositional content in the exact truthmaker semantics, featuring:
   - Verifier and falsifier sets for atomic and complex propositions
   - Classical semantic constraints (no gaps/gluts)
   - Optional semantic constraints (contingency, disjointness, etc.)
   - Truth value evaluation at possible worlds
   - Pretty printing of propositions with truth values

3. ModelStructure: Manages the overall semantic model structure, providing:
   - Z3 solver integration for constraint satisfaction
   - State space construction and management
   - Model evaluation and verification
   - Visualization and printing utilities
   - Model persistence and serialization

The semantic framework uses a bit-vector representation for states, where:
- States are represented as bit vectors
- Possible worlds are maximal consistent states
- Verification and falsification are primitive relations on states
- Complex formulas are evaluated through recursive decomposition

Key Features:
- Exact truthmaker semantics with verifiers and falsifiers
- Support for classical and non-classical logics
- Flexible constraint system for semantic properties
- Efficient state space representation using bit vectors
- Comprehensive model checking and evaluation
- Rich visualization and debugging capabilities

Dependencies:
- z3-solver: For constraint solving and model construction
- sys: For system integration and I/O
- time: For performance monitoring

The module is designed to be used as part of a larger model checking framework,
providing the semantic foundation for modal logic analysis and verification.
"""

import z3
import sys
import time

# Standard imports
from model_checker.model import (
    PropositionDefaults,
    SemanticDefaults,
    ModelDefaults,
    ModelConstraints,
)
from model_checker.utils import (
    ForAll,
    Exists,
    bitvec_to_substates,
    pretty_set_print,
    int_to_binary,
)
from model_checker import syntactic



##############################################################################
######################### SEMANTICS AND PROPOSITIONS #########################
##############################################################################

class Semantics(SemanticDefaults):
    """Default semantics implementation for the modal logic system.
    
    This class provides a concrete implementation of the semantic framework
    for modal logic, including the definition of possible worlds, compatibility
    relations, truth and falsity conditions, and frame constraints.
    
    The semantics uses a bit-vector representation of states where worlds are
    represented as maximal possible states, and the verification and falsification
    of atomic propositions is defined in terms of state-based verifiers and falsifiers.
    
    Attributes:
        DEFAULT_EXAMPLE_SETTINGS (dict): Default settings for examples using this semantics
        verify (Function): Z3 function mapping states and atoms to truth values
        falsify (Function): Z3 function mapping states and atoms to falsity values
        possible (Function): Z3 function determining if a state is possible
        main_world (BitVec): The designated world for evaluation
        frame_constraints (list): Z3 constraints defining the logical frame
        premise_behavior (function): Function defining premise behavior for validity
        conclusion_behavior (function): Function defining conclusion behavior for validity
    """

    DEFAULT_EXAMPLE_SETTINGS = {
        'N' : 3,
        'contingent' : False,
        'non_empty' : False,
        'non_null' : False,
        'disjoint' : False,
        'max_time' : 1,
        'iterate' : 1,
        'iteration_timeout': 1.0,
        'iteration_attempts': 5,
        'expectation' : None,
    }
    
    # Default general settings for the default theory
    DEFAULT_GENERAL_SETTINGS = {
        "print_impossible": False,
        "print_constraints": False,
        "print_z3": False,
        "save_output": False,
        "maximize": False,
    }

    def __init__(self, settings):

        # Initialize the superclass to set defaults
        super().__init__(settings)

        # Define the Z3 primitives
        self.verify = z3.Function("verify", z3.BitVecSort(self.N), syntactic.AtomSort, z3.BoolSort())
        self.falsify = z3.Function("falsify", z3.BitVecSort(self.N), syntactic.AtomSort, z3.BoolSort())
        self.possible = z3.Function("possible", z3.BitVecSort(self.N), z3.BoolSort())
        self.main_world = z3.BitVec("w", self.N)
        self.main_point = {
            "world" : self.main_world
        }

        # Define the frame constraints
        x, y = z3.BitVecs("frame_x frame_y", self.N)
        possibility_downard_closure = ForAll(
            [x, y],
            z3.Implies(
                z3.And(
                    self.possible(y),
                    self.is_part_of(x, y)
                ),
                self.possible(x)
            ),
        )
        is_main_world = self.is_world(self.main_world)

        # Set frame constraints
        self.frame_constraints = [
            possibility_downard_closure,
            is_main_world,
        ]

        # Define invalidity conditions
        self.premise_behavior = lambda premise: self.true_at(premise, self.main_point["world"])
        self.conclusion_behavior = lambda conclusion: self.false_at(conclusion, self.main_point["world"])

    def compatible(self, state_x, state_y):
        """Determines if the fusion of two states is possible.
        
        Args:
            state_x (BitVecRef): First state to check
            state_y (BitVecRef): Second state to check
            
        Returns:
            BoolRef: Z3 constraint expressing whether the fusion of state_x and
                    state_y is possible.
        """
        return self.possible(self.fusion(state_x, state_y))

    def maximal(self, state_w):
        """Determines if a state is maximal with respect to compatibility.
        
        A state is maximal if it includes all states that are compatible with it
        as parts. This is used to identify possible worlds in the model.
        
        Args:
            state_w (BitVecRef): The state to check for maximality
            
        Returns:
            BoolRef: Z3 constraint expressing whether state_w is maximal
        """
        x = z3.BitVec("max_x", self.N)
        return ForAll(
            x,
            z3.Implies(
                self.compatible(x, state_w),
                self.is_part_of(x, state_w),
            ),
        )

    def is_world(self, state_w):
        """Determines if a state represents a possible world in the model.
        
        A state is a possible world if it is both possible (according to the model's
        possibility function) and maximal (cannot be properly extended while maintaining
        compatibility).
        
        Args:
            state_w (BitVecRef): The state to check
            
        Returns:
            BoolRef: Z3 constraint expressing whether state_w is a possible world
        """
        return z3.And(
            self.possible(state_w),
            self.maximal(state_w),
        )

    def max_compatible_part(self, state_x, state_w, state_y):
        """Determines if state_x is the maximal part of state_w compatible with state_y.
        
        This method checks whether state_x is a largest substate of state_w that maintains
        compatibility with state_y (there may be more than one). This is used to
        determine the alternative worlds used in the counterfactual semantics.
        
        Args:
            state_x (BitVecRef): The state being tested as maximal compatible part
            state_w (BitVecRef): The state containing state_x
            state_y (BitVecRef): The state that state_x must be compatible with
            
        Returns:
            BoolRef: Z3 constraint expressing whether state_x is a maximal part
                    of state_w that is compatible with state_y
        """
        z = z3.BitVec("max_part", self.N)
        return z3.And(
            self.is_part_of(state_x, state_w),
            self.compatible(state_x, state_y),
            ForAll(
                z,
                z3.Implies(
                    z3.And(
                        self.is_part_of(z, state_w),
                        self.compatible(z, state_y),
                        self.is_part_of(state_x, z),
                    ),
                    state_x == z,
                ),
            ),
        )

    def is_alternative(self, state_u, state_y, state_w):
        """Determines if a state represents an alternative world resulting from
        imposing one state on another.
        
        This method checks whether state_u is a possible world that results from imposing state_y
        on world state_w. The alternative world must contain state_y as a part and must also
        contain a maximal part of state_w that is compatible with state_y.
        
        Args:
            state_u (BitVecRef): The state being tested as an alternative world
            state_y (BitVecRef): The state being imposed
            state_w (BitVecRef): The world state being modified
            
        Returns:
            BoolRef: Z3 constraint expressing whether state_u is an alternative world
                    resulting from imposing state_y on state_w
        """
        z = z3.BitVec("alt_z", self.N)
        return z3.And(
            self.is_world(state_u),
            self.is_part_of(state_y, state_u),
            Exists(z, z3.And(self.is_part_of(z, state_u), self.max_compatible_part(z, state_w, state_y))),
        )

    def true_at(self, sentence, eval_world):
        """Determines if a sentence is true at a given evaluation world.
        
        For atomic sentences (sentence_letters), it checks if there exists some state x 
        that is part of the evaluation world such that x verifies the sentence letter.
        
        For complex sentences, it delegates to the operator's true_at method with the 
        sentence's arguments and evaluation world.
        
        Args:
            sentence (Sentence): The sentence to evaluate
            eval_world (BitVecRef): The world at which to evaluate the sentence
            
        Returns:
            BoolRef: Z3 constraint expressing whether the sentence is true at eval_world
        """
        sentence_letter = sentence.sentence_letter
        if sentence_letter is not None:
            x = z3.BitVec("t_atom_x", self.N)
            return Exists(x, z3.And(self.is_part_of(x, eval_world), self.verify(x, sentence_letter)))
        operator = sentence.operator
        arguments = sentence.arguments or ()
        return operator.true_at(*arguments, eval_world)

    def false_at(self, sentence, eval_world):
        """Determines if a sentence is false at a given evaluation world.
        
        For atomic sentences (sentence_letters), it checks if there exists some state x 
        that is part of the evaluation world such that x falsifies the sentence letter.
        
        For complex sentences, it delegates to the operator's false_at method with the 
        sentence's arguments and evaluation world.
        
        Args:
            sentence (Sentence): The sentence to evaluate
            eval_world (BitVecRef): The world at which to evaluate the sentence
            
        Returns:
            BoolRef: Z3 constraint expressing whether the sentence is false at eval_world
        """
        sentence_letter = sentence.sentence_letter
        if sentence_letter is not None:
            x = z3.BitVec("f_atom_x", self.N)
            return Exists(x, z3.And(self.is_part_of(x, eval_world), self.falsify(x, sentence_letter)))
        operator = sentence.operator
        arguments = sentence.arguments or ()
        return operator.false_at(*arguments, eval_world)

    def extended_verify(self, state, sentence, eval_point):
        """Determines if a state verifies a sentence at an evaluation point.
        
        This method extends the hyperintensional verification relation to all
        sentences of the language in order to determine whether a specific state
        is a verifier for a given sentence at a particular evaluation point.
        
        For atomic sentences (those with a sentence_letter), it directly uses the verify
        relation to determine if the state verifies the atomic sentence.
        
        For complex sentences (those with an operator), it delegates to the operator's
        extended_verify method which handles the verification conditions specific to
        that operator.
        
        Args:
            state (BitVecRef): The state being tested as a verifier
            sentence (Sentence): The sentence to check
            eval_point (dict): The evaluation point context
            
        Returns:
            BoolRef: Z3 constraint expressing the verification condition
        """
        sentence_letter = sentence.sentence_letter
        if sentence_letter is not None:
            return self.verify(state, sentence_letter)
        operator = sentence.operator
        arguments = sentence.arguments or ()
        return operator.extended_verify(state, *arguments, eval_point)
    
    def extended_falsify(self, state, sentence, eval_point):
        """Determines if a state falsifies a sentence at an evaluation point.
        
        This method extends the hyperintensional falsification relation to all
        sentences of the language in order to determine whether a specific state
        is a falsifier for a given sentence at a particular evaluation point.
        
        For atomic sentences (those with a sentence_letter), it directly uses the falsify
        relation to determine if the state falsifies the atomic sentence.
        
        For complex sentences (those with an operator), it delegates to the operator's
        extended_falsify method which handles the falsification conditions specific to
        that operator.
        
        Args:
            state (BitVecRef): The state being tested as a falsifier
            sentence (Sentence): The sentence to check
            eval_point (dict): The evaluation point context
            
        Returns:
            BoolRef: Z3 constraint expressing the falsification condition
        """
        sentence_letter = sentence.sentence_letter
        if sentence_letter is not None:
            return self.falsify(state, sentence_letter)
        operator = sentence.operator
        arguments = sentence.arguments or ()
        return operator.extended_falsify(state, *arguments, eval_point)

    def calculate_alternative_worlds(self, verifiers, eval_point, model_structure):
        """Calculates alternative worlds where a given state is imposed.
        
        This method identifies all alternative worlds generated by the verifiers
        and evaluation world. These alternative worlds are used in the semantics
        for counterfactual conditionals.
        
        Args:
            verifiers (set): Set of states verifying the antecedent
            eval_point (dict): The evaluation point containing the reference world
            model_structure (ModelStructure): The model being evaluated
            
        Returns:
            set: Set of alternative worlds where the antecedent is true
        """
        is_alt = model_structure.semantics.is_alternative
        eval = model_structure.z3_model.evaluate
        world_states = model_structure.z3_world_states
        eval_world = eval_point["world"]
        return {
            pw for ver in verifiers
            for pw in world_states
            if eval(is_alt(pw, ver, eval_world))
        }

    def calculate_outcome_worlds(self, verifiers, eval_point, model_structure):
        """Calculates outcome worlds that result from an imposition.
        
        This method identifies all worlds that result from imposing a state on
        the evaluation world using the primitive imposition relation rather than
        the alternative world relation where the later is defined. These worlds
        are used in the semantics of the imposition operator.
        
        Args:
            verifiers (set): Set of states being imposed
            eval_point (dict): The evaluation point containing the reference world
            model_structure (ModelStructure): The model being evaluated
            
        Returns:
            set: Set of outcome worlds resulting from the imposition
        """
        imposition = model_structure.semantics.imposition
        eval = model_structure.z3_model.evaluate
        world_states = model_structure.world_states
        eval_world = eval_point["world"]
        return {
            pw for ver in verifiers
            for pw in world_states
            if eval(imposition(ver, eval_world, pw))
        }
        

class Proposition(PropositionDefaults):
    """Concrete implementation of propositions for the default semantic theory.
    
    This class represents the propositional content of sentences in the model,
    defining how they are verified and falsified by states. It implements the
    exact-truthmaker semantics approach where each proposition is identified
    with a pair of sets: verifiers (states that make it true) and falsifiers
    (states that make it false).
    
    The class handles constraint generation for atomic propositions and
    provides methods for testing truth values at evaluation points.
    
    Attributes:
        verifiers (set): States that verify the proposition
        falsifiers (set): States that falsify the proposition
        eval_world: The world at which the proposition is being evaluated
    """

    def __init__(self, sentence, model_structure, eval_world='main'):
        """Initialize a Proposition instance.

        Args:
            sentence (Sentence): The sentence whose proposition is being represented
            model_structure (ModelStructure): The model structure containing semantic definitions
            eval_world (str|BitVecRef, optional): The world at which to evaluate the proposition.
                If 'main', uses the model's main world. Defaults to 'main'.
        """

        super().__init__(sentence, model_structure)

        self.eval_world = model_structure.main_point["world"] if eval_world == 'main' else eval_world
        self.verifiers, self.falsifiers = self.find_proposition()
        
    def __eq__(self, other):
        """Compare two propositions for equality.
        
        Two propositions are considered equal if they have the same verifiers,
        falsifiers, and name.
        
        Args:
            other (Proposition): The proposition to compare with
            
        Returns:
            bool: True if the propositions are equal, False otherwise
        """
        return (
            self.verifiers == other.verifiers
            and self.falsifiers == other.falsifiers
            and self.name == other.name
        )

    def __repr__(self):
        """Return a string representation of the proposition.
        
        Returns a string showing the verifiers and falsifiers of the proposition
        in set notation. Only includes possible states unless print_impossible
        setting is enabled.
        
        Returns:
            str: A string of the form "< {verifiers}, {falsifiers} >" where each
                set contains the binary representations of the states
        """
        N = self.model_structure.model_constraints.semantics.N
        possible = self.model_structure.model_constraints.semantics.possible
        z3_model = self.model_structure.z3_model
        ver_states = {
            bitvec_to_substates(bit, N)
            for bit in self.verifiers
            if z3_model.evaluate(possible(bit)) or self.settings['print_impossible']
        }
        fal_states = {
            bitvec_to_substates(bit, N)
            for bit in self.falsifiers
            if z3_model.evaluate(possible(bit)) or self.settings['print_impossible']
        }
        return f"< {pretty_set_print(ver_states)}, {pretty_set_print(fal_states)} >"

    def proposition_constraints(self, sentence_letter):
        """Generates Z3 constraints for a sentence letter based on semantic settings.

        This method generates constraints that govern the behavior of atomic propositions
        in the model. It includes:
        - Classical constraints (preventing truth value gaps and gluts)
        - Optional constraints based on settings:
            - non-null: Prevents null states from verifying/falsifying
            - contingent: Ensures propositions have both possible verifiers and falsifiers
            - disjoint: Ensures atomic propositions have disjoint verifiers/falsifiers

        Returns:
            list: A list of Z3 constraints for the sentence letter
        """
        semantics = self.semantics

        def get_classical_constraints():
            x, y = z3.BitVecs("cl_prop_x cl_prop_y", semantics.N)
            """Generate constraints that enforce classical behavior by ruling out
            truth value gaps and gluts.
            
            These constraints ensure:
            1. If two states verify a proposition, their fusion also verifies it
            2. If two states falsify a proposition, their fusion also falsifies it  
            3. No state can both verify and falsify a proposition (no gluts)
            4. Every possible state must be compatible with either a verifier or falsifier (no gaps)
            """
            verifier_fusion_closure = ForAll(
                [x, y],
                z3.Implies(
                    z3.And(
                        semantics.verify(x, sentence_letter),
                        semantics.verify(y, sentence_letter)
                    ),
                    semantics.verify(semantics.fusion(x, y), sentence_letter),
                ),
            )
            falsifier_fusion_closure = ForAll(
                [x, y],
                z3.Implies(
                    z3.And(
                        semantics.falsify(x, sentence_letter),
                        semantics.falsify(y, sentence_letter)
                    ),
                    semantics.falsify(semantics.fusion(x, y), sentence_letter),
                ),
            )
            no_glut = ForAll(
                [x, y],
                z3.Implies(
                    z3.And(
                        semantics.verify(x, sentence_letter),
                        semantics.falsify(y, sentence_letter)
                    ),
                    z3.Not(semantics.compatible(x, y)),
                ),
            )
            no_gap = ForAll(
                x,
                z3.Implies(
                    semantics.possible(x),
                    Exists(
                        y,
                        z3.And(
                            semantics.compatible(x, y),
                            z3.Or(
                                semantics.verify(y, sentence_letter),
                                semantics.falsify(y, sentence_letter)
                            ),
                        ),
                    ),
                ),
            )
            return [
                verifier_fusion_closure,
                falsifier_fusion_closure,
                no_glut,
                no_gap
            ]

        def get_non_empty_constraints():
            """The non_empty constraints ensure that each atomic proposition has at least one
            verifier and one falsifier. While these constraints are implied by the contingent
            constraints, they are included separately to prevent trivial satisfaction of the
            disjoint constraints when contingent constraints are not enabled."""
            x, y = z3.BitVecs("ct_empty_x ct_empty_y", semantics.N)
            return [
                z3.Exists(
                    [x, y],
                    z3.And(
                        semantics.verify(x, sentence_letter),
                        semantics.falsify(y, sentence_letter)
                    )
                )
            ]

        def get_non_null_constraints():
            """The non_null constraints prevent null states (empty states) from being verifiers
            or falsifiers. These constraints are important to prevent trivial satisfaction of
            the disjoint constraints, though they are already entailed by the contingent constraints
            when those are enabled."""
            return [
                z3.Not(semantics.verify(0, sentence_letter)),
                z3.Not(semantics.falsify(0, sentence_letter)),
            ]

        def get_contingent_constraints():
            """The contingent constraints ensure that each atomic proposition has
            at least one possible verifier and one possible falsifier, which implicitly
            guarantees that no null states are verifiers or falsifiers."""
            x, y = z3.BitVecs("ct_cont_x ct_cont_y", semantics.N)
            possible_verifier = Exists(
                x,
                z3.And(semantics.possible(x), semantics.verify(x, sentence_letter))
            )
            possible_falsifier = Exists(
                y,
                z3.And(semantics.possible(y), semantics.falsify(y, sentence_letter))
            )
            return [
                possible_verifier,
                possible_falsifier,
            ]

        def get_disjoint_constraints():
            """The disjoint constraints ensure that atomic propositions have
            non-overlapping verifiers and falsifiers. This includes non-null
            constraints to prevent empty states from being verifiers or falsifiers."""
            x, y, z = z3.BitVecs("dj_prop_x dj_prop_y dj_prop_z", semantics.N)
            disjoint_constraints = []
            for other_letter in self.sentence_letters:
                if other_letter is not sentence_letter:
                    other_disjoint_atom = ForAll(
                        [x, y],
                        z3.Implies(
                            z3.And(
                                semantics.non_null_part_of(x, y),
                                z3.Or(
                                    semantics.verify(y, sentence_letter),
                                    semantics.falsify(y, sentence_letter),
                                ),
                            ),
                            ForAll(
                                z,
                                z3.Implies(
                                    z3.Or(
                                        semantics.verify(z, other_letter),
                                        semantics.falsify(z, other_letter)
                                    ),
                                    z3.Not(semantics.is_part_of(x, z)),
                                )
                            )
                        )
                    )
                    disjoint_constraints.append(other_disjoint_atom)
            return disjoint_constraints

        # Collect constraints
        constraints = get_classical_constraints()
        if self.settings['contingent']:
            constraints.extend(get_contingent_constraints())
        if self.settings['non_empty'] and not self.settings['contingent']:
            constraints.extend(get_non_empty_constraints())
        if self.settings['disjoint']:
            constraints.extend(get_disjoint_constraints())
            constraints.extend(get_non_null_constraints())
        if self.settings['non_null'] and not self.settings['disjoint']:
            constraints.extend(get_non_null_constraints())
        return constraints

    def find_proposition(self):
        """Computes the verifier and falsifier sets for this proposition.
        
        This method determines the sets of states that verify and falsify
        the proposition in the model. For atomic propositions, it uses the
        verify and falsify relations; for complex propositions, it delegates
        to the appropriate operator's implementation.
        
        Returns:
            tuple: A pair (verifiers, falsifiers) containing the sets of
                 states that verify and falsify the proposition respectively
        """
        model = self.model_structure.z3_model
        semantics = self.semantics
        eval_world = self.eval_world
        operator = self.operator
        arguments = self.arguments or ()
        sentence_letter = self.sentence_letter
        if sentence_letter is not None:
            V = {
                state for state in self.model_structure.all_states
                if model.evaluate(semantics.verify(state, sentence_letter))
            }
            F = {
                state for state in self.model_structure.all_states
                if model.evaluate(semantics.falsify(state, sentence_letter))
            }
            return V, F
        if operator is not None:
            return operator.find_verifiers_and_falsifiers(*arguments, eval_world)
        raise ValueError(f"Their is no proposition for {self}.")

    def truth_value_at(self, eval_world):
        """Determines the truth value of the proposition at a given world.
        
        Checks if the world contains a verifier for the proposition (making it true)
        or a falsifier (making it false). Also checks for potential inconsistencies
        where a world contains both a verifier and falsifier, which should not occur
        in a well-formed model.
        
        Args:
            eval_world (BitVecRef): The world at which to evaluate the proposition
            
        Returns:
            bool: True if the world contains a verifier, False if it contains a falsifier
            
        Note:
            Prints a warning if an inconsistency is detected where a world contains
            both a verifier and falsifier for the same proposition.
        """
        semantics = self.model_structure.model_constraints.semantics
        z3_model = self.model_structure.z3_model
        ver_witness = None
        fal_witness = None
        exists_verifier = False
        exists_falsifier = False
        for verifier in self.verifiers:
            if z3_model.evaluate(semantics.is_part_of(verifier, eval_world)):
                ver_witness = verifier
                exists_verifier = True
                break
        for falsifier in self.falsifiers:
            if z3_model.evaluate(semantics.is_part_of(falsifier, eval_world)):
                fal_witness = falsifier
                exists_falsifier = True
                break
        if exists_verifier == exists_falsifier:
            print( # NOTE: a warning is preferable to raising an error
                f"WARNING: the world {bitvec_to_substates(eval_world, self.N)} contains both:\n "
                f"  The verifier {bitvec_to_substates(ver_witness, self.N)}; and"
                f"  The falsifier {bitvec_to_substates(fal_witness, self.N)}."
            )
        return exists_verifier

    def print_proposition(self, eval_point, indent_num, use_colors):
        """Print the proposition with its truth value at the given evaluation point.

        Prints the proposition name, its verifiers and falsifiers, and its truth value
        at the specified evaluation world. The output is formatted with optional
        indentation and color coding.

        Args:
            eval_point (dict): Dictionary containing evaluation context, including the 'world' key
            indent_num (int): Number of indentation levels to use
            use_colors (bool): Whether to use ANSI color codes in the output

        Returns:
            None
        """
        N = self.model_structure.model_constraints.semantics.N
        eval_world = eval_point["world"]
        truth_value = self.truth_value_at(eval_world)
        world_state = bitvec_to_substates(eval_world, N)
        RESET, FULL, PART = self.set_colors(self.name, indent_num, truth_value, world_state, use_colors)
        print(
            f"{'  ' * indent_num}{FULL}|{self.name}| = {self}{RESET}"
            f"  {PART}({truth_value} in {world_state}){RESET}"
        )


class ModelStructure(ModelDefaults):
    """Constructs a semantic model from a Z3 model over which to interpret the language.

    This class represents the core model structure used for semantic evaluation,
    including the state space, possible worlds, and evaluation functions. It manages
    the Z3 solver instance and provides methods for model construction, evaluation,
    and visualization.

    Attributes:
        main_world (BitVecRef): The designated world for evaluation
        z3_main_world (BitVecRef): Z3 model value for the main world
        z3_possible_states (list): List of all possible states in the Z3 model
        z3_world_states (list): List of all world states in the Z3 model
        main_point (dict): Dictionary containing evaluation context with the main world

    The class provides functionality for:
    - Initializing and managing the model structure
    - Evaluating formulas in the model
    - Printing model information and evaluation results
    - Saving model data to files
    - Handling model constraints and satisfiability checking
    """

    def __init__(self, model_constraints, settings):
        """Initialize ModelStructure with model constraints and optional max time.
        
        Args:
            model_constraints: ModelConstraints object containing all constraints
            max_time: Maximum time in seconds to allow for solving. Defaults to 1.
        """
        if not isinstance(model_constraints, ModelConstraints):
            raise TypeError(
                f"Expected model_constraints to be a ModelConstraints object, got {type(model_constraints)}. "
                "Make sure you're passing the correct model_constraints object."
            )

        super().__init__(model_constraints, settings)

        # Get main point
        self.main_world = self.main_point["world"]

        # Initialize Z3 model values
        self.z3_main_world = None
        self.z3_possible_states = None
        self.z3_world_states = None 
        
        # Initialize attributes for difference tracking
        self.model_differences = None  # Will store differences with previous model
        self.previous_model = None     # Reference to previous model for comparison

        # Only evaluate if we have a valid model
        if self.z3_model_status and self.z3_model is not None:
            self.z3_main_world = self.z3_model[self.main_world]
            self.main_point["world"] = self.z3_main_world
            self.z3_possible_states = [
                bit
                for bit in self.all_states
                if bool(self.z3_model.evaluate(self.semantics.possible(bit)))
            ]
            self.z3_world_states = [
                bit
                for bit in self.z3_possible_states
                if bool(self.z3_model.evaluate(self.semantics.is_world(bit)))
            ]

    def print_evaluation(self, output=sys.__stdout__):
        """Print the evaluation world and evaluate all sentence letters at that world.
        
        Displays the binary representation of the evaluation world and indicates which
        atomic sentences (sentence letters) are true or false at that world in the model.
        
        Args:
            output (file object, optional): Output stream to write to. Defaults to sys.stdout.
        """
        BLUE = ""
        RESET = ""
        main_world = self.main_point["world"]
        if output is sys.__stdout__:
            BLUE = "\033[34m"
            RESET = "\033[0m"
        print(
            f"\nThe evaluation world is: {BLUE}{bitvec_to_substates(main_world, self.N)}{RESET}\n",
            file=output,
        )

    def print_states(self, output=sys.__stdout__):
        """Print all states in the model with their binary representations and properties.
        
        Prints each state in the model along with its binary representation and additional
        properties like whether it's a world state, possible state, or impossible state.
        States are color-coded when printing to stdout:
        - World states are marked with "(world)"
        - Possible states are highlighted
        - Impossible states are shown only if print_impossible setting is True
        - The null state (0) is specially formatted
        
        Args:
            output (file object, optional): Output stream to write to. Defaults to sys.stdout.
        """

        def binary_bitvector(bit):
            """Convert a Z3 BitVec to its binary string representation.
            
            For BitVecs whose size is not divisible by 4, returns the raw sexpr.
            For BitVecs whose size is divisible by 4, converts the hexadecimal
            representation to binary format.
            
            Args:
                bit (BitVecRef): The Z3 BitVec to convert
                
            Returns:
                str: Binary string representation of the BitVec
            """
            return (
                bit.sexpr()
                if self.N % 4 != 0
                else int_to_binary(int(bit.sexpr()[2:], 16), self.N)
            )
        
        def format_state(bin_rep, state, color, label=""):
            """Format and print a state with optional label and color formatting.
            
            Args:
                bin_rep (str): Binary representation of the state
                state (str): State representation
                color (str): ANSI color code for formatting
                label (str, optional): Additional label to append to state. Defaults to empty string.
                
            Returns:
                None: Prints the formatted state to the specified output
            """
            label_str = f" ({label})" if label else ""
            use_colors = output is sys.__stdout__
            if use_colors:
                print(f"  {self.WHITE}{bin_rep} = {color}{state}{label_str}{self.RESET}", file=output)
            else:
                print(f"  {bin_rep} = {state}{label_str}", file=output)
        
        # Print formatted state space
        print("State Space:", file=output)
        for bit in self.all_states:
            state = bitvec_to_substates(bit, self.N)
            bin_rep = binary_bitvector(bit)
            if bit == 0:
                format_state(bin_rep, state, self.COLORS["initial"])
            elif bit in self.z3_world_states:
                format_state(bin_rep, state, self.COLORS["world"], "world")
            elif bit in self.z3_possible_states:
                format_state(bin_rep, state, self.COLORS["possible"])
            elif self.settings['print_impossible']:
                format_state(bin_rep, state, self.COLORS["impossible"], "impossible")

    def print_all(self, default_settings, example_name, theory_name, output=sys.__stdout__):
        """Print a complete overview of the model structure and evaluation results.
        
        This method provides a comprehensive display of the model, including:
        - Model states and their properties
        - Evaluation results at the designated world
        - Truth values of atomic sentence letters
        - Recursive evaluation of complex sentences and their subformulas
        
        Args:
            default_settings (dict): Default configuration settings for the model
            example_name (str): Name of the example being evaluated
            theory_name (str): Name of the logical theory being used
            output (file, optional): Output stream to write to. Defaults to sys.stdout
        """
        model_status = self.z3_model_status
        self.print_info(model_status, self.settings, example_name, theory_name, output)
        if model_status:
            self.print_states(output)
            self.print_evaluation(output)
            self.print_input_sentences(output)
            self.print_model(output)
            if output is sys.__stdout__:
                total_time = round(time.time() - self.start_time, 4) 
                print(f"Total Run Time: {total_time} seconds\n", file=output)
                print(f"{'='*40}", file=output)
            return

    def print_to(self, default_settings, example_name, theory_name, print_constraints=None, output=sys.__stdout__):
        """Print the model details to the specified output stream.

        This method prints all elements of the model including states, evaluation results,
        and optionally constraints to the provided output stream.

        Args:
            default_settings (dict): Default configuration settings for the model
            example_name (str): Name of the example being evaluated
            theory_name (str): Name of the logical theory being used
            print_constraints (bool, optional): Whether to print model constraints.
                Defaults to the value in self.settings.
            output (TextIO, optional): Output stream to write to. Defaults to sys.stdout.
        """
        if print_constraints is None:
            print_constraints = self.settings["print_constraints"]
        # Check if we actually timed out (runtime >= max_time)
        actual_timeout = hasattr(self, 'z3_model_runtime') and self.z3_model_runtime is not None and self.z3_model_runtime >= self.max_time
        
        # Only show timeout if we really timed out and didn't find a model
        if actual_timeout and (not hasattr(self, 'z3_model') or self.z3_model is None):
            print(f"\nTIMEOUT: Model search exceeded maximum time of {self.max_time} seconds", file=output)
            print(f"No model for example {example_name} found before timeout.", file=output)
            print(f"Try increasing max_time > {self.max_time}.\n", file=output)
        self.print_all(self.settings, example_name, theory_name, output)
        
        if print_constraints and self.unsat_core is not None:
            self.print_grouped_constraints(output)

    def get_world_properties(self, world, z3_model):
        """Get properties of a specific world for graph representation.
        
        This method extracts relevant properties from a world state that are
        used for isomorphism checking. This helps identify structurally
        equivalent worlds across different models.
        
        Args:
            world: The world state to analyze
            z3_model: The current Z3 model
            
        Returns:
            dict: Dictionary of world properties
        """
        properties = {}
        
        # Check if this is the main world
        if z3_model.evaluate(world == self.main_point["world"]):
            properties["is_main_world"] = True
            
        # Add other theory-specific properties
        try:
            # Check if this is a maximal world
            if hasattr(self.semantics, 'maximal'):
                properties["is_maximal"] = bool(z3_model.evaluate(self.semantics.maximal(world)))
                
            # Check world size (number of set bits)
            from model_checker.utils import bitvec_to_substates
            substate_repr = bitvec_to_substates(world, self.semantics.N)
            set_bits = substate_repr.count('1')
            properties["size"] = set_bits
            
        except Exception as e:
            # Log any errors but don't fail
            import logging
            logger = logging.getLogger(__name__)
            logger.debug(f"Error getting properties for world {world}: {str(e)}")
        
        return properties
    
    def get_relation_edges(self, z3_model):
        """Get theory-specific relation edges for graph representation.
        
        This method extracts any additional relations between worlds
        beyond the basic accessibility relation. This helps with
        isomorphism checking by capturing all structural relations.
        
        Args:
            z3_model: The current Z3 model
            
        Returns:
            list: List of tuples (source, target, attributes) for additional edges
        """
        extra_edges = []
        
        try:
            # Get world states
            world_states = self.z3_world_states
            if not world_states:
                return extra_edges
                
            # Map world states to indices for graph representation
            world_to_idx = {str(world): i for i, world in enumerate(world_states)}
            
            # Add edges for semantic relations if available
            # For example, if there's a compatibility relation:
            if hasattr(self.semantics, 'compatible'):
                for i, w1 in enumerate(world_states):
                    for j, w2 in enumerate(world_states):
                        if i != j:  # Don't check self-compatibility
                            try:
                                is_compatible = bool(z3_model.evaluate(self.semantics.compatible(w1, w2)))
                                if is_compatible:
                                    extra_edges.append((i, j, {"relation": "compatible"}))
                            except Exception:
                                pass
                                
        except Exception as e:
            # Log any errors but don't fail
            import logging
            logger = logging.getLogger(__name__)
            logger.debug(f"Error getting relation edges: {str(e)}")
                
        return extra_edges
    
    def _get_verifier_falsifier_states(self, letter):
        """Get the verifier and falsifier states for a sentence letter.
        
        Args:
            letter: The sentence letter to check
            
        Returns:
            tuple: (verifier_states, falsifier_states) as sets of state strings
        """
        from model_checker.utils import bitvec_to_substates, pretty_set_print
        
        N = self.semantics.N
        z3_model = self.z3_model
        possible = self.semantics.possible
        verify = self.semantics.verify
        falsify = self.semantics.falsify
        print_impossible = self.settings.get('print_impossible', False)
        
        verifier_states = set()
        falsifier_states = set()
        
        for state in self.all_states:
            try:
                # Check if this state is possible
                is_possible = bool(z3_model.evaluate(possible(state)))
                
                # Include the state if it's possible or if print_impossible is enabled
                if is_possible or print_impossible:
                    # Check if this state verifies the letter
                    if bool(z3_model.evaluate(verify(state, letter))):
                        state_name = bitvec_to_substates(state, N)
                        verifier_states.add(state_name)
                        
                    # Check if this state falsifies the letter
                    if bool(z3_model.evaluate(falsify(state, letter))):
                        state_name = bitvec_to_substates(state, N)
                        falsifier_states.add(state_name)
            except Exception:
                pass
                
        return verifier_states, falsifier_states
        
    def detect_model_differences(self, previous_structure):
        """Calculate differences between this model and a previous one.
        
        This method detects differences between models with the default theory's semantics:
        - Possible states and world states
        - Verification and falsification of atomic propositions
        - Part-whole relationships (is_part_of function)
        - Other semantic function interpretations
        
        Args:
            previous_structure: The previous model to compare against
            
        Returns:
            dict: Structured differences between models
        """
        if not hasattr(previous_structure, 'z3_model') or previous_structure.z3_model is None:
            return None
            
        # Initialize differences structure with default theory's specific categories
        differences = {
            "sentence_letters": {},  # Changed propositions
            "worlds": {             # Changes in world states
                "added": [],
                "removed": []
            },
            "possible_states": {    # Changes in possible states
                "added": [],
                "removed": []
            },
            "parthood": {}          # Changes in part-whole relationships
        }
        
        # Get Z3 models
        new_model = self.z3_model
        prev_model = previous_structure.z3_model
        
        # Compare possible states
        try:
            prev_possible = set(getattr(previous_structure, 'z3_possible_states', []))
            new_possible = set(getattr(self, 'z3_possible_states', []))
            
            added_possible = new_possible - prev_possible
            removed_possible = prev_possible - new_possible
            
            if added_possible:
                differences["possible_states"]["added"] = list(added_possible)
            if removed_possible:
                differences["possible_states"]["removed"] = list(removed_possible)
            
            # Compare world states
            prev_worlds = set(getattr(previous_structure, 'z3_world_states', []))
            new_worlds = set(getattr(self, 'z3_world_states', []))
            
            added_worlds = new_worlds - prev_worlds
            removed_worlds = prev_worlds - new_worlds
            
            if added_worlds:
                differences["worlds"]["added"] = list(added_worlds)
            if removed_worlds:
                differences["worlds"]["removed"] = list(removed_worlds)
                
            # Check for part-whole relationship changes (specific to default theory)
            if hasattr(self.semantics, 'is_part_of'):
                parthood_changes = {}
                # Sample a subset of state pairs to check for parthood changes
                for x in self.z3_possible_states[:10]:  # Limit to avoid too much computation
                    for y in self.z3_possible_states[:10]:
                        if x == y:
                            continue
                        try:
                            old_parthood = bool(prev_model.evaluate(self.semantics.is_part_of(x, y)))
                            new_parthood = bool(new_model.evaluate(self.semantics.is_part_of(x, y)))
                            
                            if old_parthood != new_parthood:
                                key = f"{bitvec_to_substates(x, self.semantics.N)}, {bitvec_to_substates(y, self.semantics.N)}"
                                parthood_changes[key] = {
                                    "old": old_parthood,
                                    "new": new_parthood
                                }
                        except Exception:
                            pass
                
                if parthood_changes:
                    differences["parthood"] = parthood_changes
                    
            # We no longer collect compatibility changes to save computational resources
        except Exception as e:
            # Log but continue with other difference detection
            print(f"Error comparing state differences: {e}")
        
        # Compare sentence letter valuations with default theory's semantics
        letter_differences = self._calculate_proposition_differences(previous_structure)
        if letter_differences:
            differences["sentence_letters"] = letter_differences
        
        # If no meaningful differences found, return None to signal fallback to basic detection
        if (not differences["sentence_letters"] and
            not differences["worlds"]["added"] and not differences["worlds"]["removed"] and
            not differences["possible_states"]["added"] and not differences["possible_states"]["removed"] and
            not differences.get("parthood")):
            return None
            
        return differences

    def _calculate_proposition_differences(self, previous_structure):
        """Calculate differences in proposition valuations between models.
        
        This is a helper method for calculate_model_differences that specifically
        focuses on changes in how atomic propositions are verified and falsified.
        
        Args:
            previous_structure: The previous model structure
            
        Returns:
            dict: Mapping from proposition names to differences in verifiers/falsifiers
        """
        from model_checker.utils import bitvec_to_substates
        letter_diffs = {}
        
        for letter in self.model_constraints.sentence_letters:
            # Get current verifiers and falsifiers
            current_verifiers, current_falsifiers = self._get_verifier_falsifier_states(letter)
            
            # Get previous verifiers and falsifiers
            prev_verifiers, prev_falsifiers = previous_structure._get_verifier_falsifier_states(letter)
            
            # Check if there are differences
            if current_verifiers != prev_verifiers or current_falsifiers != prev_falsifiers:
                letter_diffs[str(letter)] = {
                    "verifiers": {
                        "old": prev_verifiers,
                        "new": current_verifiers,
                        "added": current_verifiers - prev_verifiers,
                        "removed": prev_verifiers - current_verifiers
                    },
                    "falsifiers": {
                        "old": prev_falsifiers,
                        "new": current_falsifiers,
                        "added": current_falsifiers - prev_falsifiers,
                        "removed": prev_falsifiers - current_falsifiers
                    }
                }
        
        return letter_diffs

    # TODO: move theory specific iterate methods to default/semantic.py
    def format_model_differences(self, differences, output=sys.stdout):
        """Format and print the differences between models using default theory's semantics.
        
        This method displays the specific changes between models using the default theory's
        concepts of states, worlds, part-whole relationships, and verifier/falsifier sets.
        
        Args:
            differences: Structured differences as returned by detect_model_differences
            output (file, optional): Output stream to write to. Defaults to sys.stdout.
        """
        from model_checker.utils import bitvec_to_substates, pretty_set_print
        
        if not differences:
            print("No differences detected between models.", file=output)
            return
        
        # Print header with newlines for clear separation
        print("\n=== DIFFERENCES FROM PREVIOUS MODEL ===\n", file=output)
        
        # Store differences temporarily to use existing helper methods
        self.temp_differences = differences
        
        # Print world and state changes
        self._print_state_changes(output)
        
        # Print proposition changes 
        self._print_proposition_differences(output)
        
        # Print relation changes specific to default theory
        self._print_relation_differences(output)
        
        # Clean up the temporary storage
        delattr(self, 'temp_differences')

    def _print_state_changes(self, output=sys.stdout):
        """Print changes to the state space using default theory's format and colors."""
        from model_checker.utils import bitvec_to_substates
        diffs = getattr(self, 'temp_differences', self.model_differences)
        
        # Print world changes
        worlds = diffs.get("worlds", {})
        if worlds.get("added") or worlds.get("removed"):
            print("World Changes:", file=output)
            
            # Added worlds with world coloring
            for world in worlds.get("added", []):
                state_repr = bitvec_to_substates(world, self.semantics.N)
                print(f"  + {self.COLORS['world']}{state_repr} (world){self.RESET}", file=output)
                
            # Removed worlds with world coloring
            for world in worlds.get("removed", []):
                state_repr = bitvec_to_substates(world, self.semantics.N)
                print(f"  - {self.COLORS['world']}{state_repr} (world){self.RESET}", file=output)
        
        # Print possible state changes
        possible = diffs.get("possible_states", {})
        impossible_added = []
        impossible_removed = []
        
        # Filter possible and impossible states
        possible_added = []
        possible_removed = []
        
        for state in possible.get("added", []):
            if bool(self.z3_model.evaluate(self.semantics.possible(state))):
                possible_added.append(state)
            else:
                impossible_added.append(state)
                
        for state in possible.get("removed", []):
            # Need to use previous model for evaluating removed states
            if hasattr(self, 'previous_model') and self.previous_model and hasattr(self.previous_model, 'z3_model'):
                if bool(self.previous_model.z3_model.evaluate(self.semantics.possible(state))):
                    possible_removed.append(state)
                else:
                    impossible_removed.append(state)
            else:
                possible_removed.append(state)  # Default to possible if can't check
        
        # Print possible state changes
        if possible_added or possible_removed:
            print("\nPossible State Changes:", file=output)
            
            # Added possible states with possible coloring
            for state in possible_added:
                state_repr = bitvec_to_substates(state, self.semantics.N)
                print(f"  + {self.COLORS['possible']}{state_repr}{self.RESET}", file=output)
                
            # Removed possible states
            for state in possible_removed:
                state_repr = bitvec_to_substates(state, self.semantics.N)
                print(f"  - {self.COLORS['possible']}{state_repr}{self.RESET}", file=output)
                
        # Print impossible state changes only if print_impossible is enabled
        if self.settings.get('print_impossible', False) and (impossible_added or impossible_removed):
            print("\nImpossible State Changes:", file=output)
            
            # Added impossible states with impossible coloring
            for state in impossible_added:
                state_repr = bitvec_to_substates(state, self.semantics.N)
                print(f"  + {self.COLORS['impossible']}{state_repr} (impossible){self.RESET}", file=output)
                
            # Removed impossible states with impossible coloring
            for state in impossible_removed:
                state_repr = bitvec_to_substates(state, self.semantics.N)
                print(f"  - {self.COLORS['impossible']}{state_repr} (impossible){self.RESET}", file=output)

    def _print_proposition_differences(self, output=sys.stdout):
        """Print changes to proposition valuations using default theory's format."""
        from model_checker.utils import pretty_set_print
        diffs = getattr(self, 'temp_differences', self.model_differences)
        letters = diffs.get("sentence_letters", {})
        if not letters:
            return
        
        print("\nProposition Changes:", file=output)
        for letter_str, changes in letters.items():
            # Get a user-friendly name for the letter
            friendly_name = self._get_friendly_letter_name(letter_str)
            print(f"  {friendly_name}:", file=output)
            
            # Print verifier changes
            if "verifiers" in changes:
                ver_changes = changes["verifiers"]
                print(f"    Verifiers: {pretty_set_print(ver_changes['new'])}", file=output)
                
                if ver_changes.get("added"):
                    print(f"      + {self.COLORS['possible']}{pretty_set_print(ver_changes['added'])}{self.RESET}", file=output)
                if ver_changes.get("removed"):
                    print(f"      - {self.COLORS['possible']}{pretty_set_print(ver_changes['removed'])}{self.RESET}", file=output)
            
            # Print falsifier changes
            if "falsifiers" in changes:
                fal_changes = changes["falsifiers"]
                print(f"    Falsifiers: {pretty_set_print(fal_changes['new'])}", file=output)
                
                if fal_changes.get("added"):
                    print(f"      + {self.COLORS['possible']}{pretty_set_print(fal_changes['added'])}{self.RESET}", file=output)
                if fal_changes.get("removed"):
                    print(f"      - {self.COLORS['possible']}{pretty_set_print(fal_changes['removed'])}{self.RESET}", file=output)

    def _print_relation_differences(self, output=sys.stdout):
        """Print changes to relations specific to the default theory."""
        diffs = getattr(self, 'temp_differences', self.model_differences)
        
        # Print part-whole relationship changes
        if diffs.get("parthood"):
            print("\nPart-Whole Relationship Changes:", file=output)
            for pair, change in diffs["parthood"].items():
                status = "now part of" if change["new"] else "no longer part of"
                print(f"  {pair}: {status}", file=output)
        
    def _get_friendly_letter_name(self, letter_str):
        """Convert a letter representation to a user-friendly name."""
        if "AtomSort!val!" in letter_str:
            # Try to convert to a letter name (A, B, C, etc.)
            try:
                idx = int(letter_str.split("AtomSort!val!")[-1])
                if 0 <= idx < 26:
                    return chr(65 + idx)  # A-Z for first 26 letters
                else:
                    return f"p{idx}"  # p0, p1, etc. for others
            except ValueError:
                pass
        return letter_str
        
    def get_structural_constraints(self, z3_model):
        """Generate constraints that force structural differences in the model.
        
        This method creates Z3 constraints that, when added to the solver,
        will force the next model to have a different structure from the
        current one. These include constraints on world counts, state organization,
        and verification/falsification patterns.
        
        Args:
            z3_model: The current Z3 model to differ from
            
        Returns:
            list: List of Z3 constraints that force structural differences
        """
        constraints = []
        
        try:
            semantics = self.semantics
            
            # 1. Force a different structure for possible states
            possible_states = self.z3_possible_states or []
            possible_state_count = len(possible_states)
            
            # Force a different number of possible states
            possible_count_expr = z3.IntVal(0)
            for state in self.all_states:
                possible_count_expr = z3.If(semantics.possible(state), possible_count_expr + 1, possible_count_expr)
            
            constraints.append(possible_count_expr != possible_state_count)
            
            # 2. Force a different arrangement of states and worlds
            if len(possible_states) > 0:
                for state in possible_states[:3]:  # Limit to first few states to avoid too many constraints
                    # Flip is_world status for some states
                    is_world_val = bool(z3_model.eval(semantics.is_world(state), model_completion=True))
                    constraints.append(semantics.is_world(state) != is_world_val)
                    
                    # Flip possibility status for some states not in possible_states
                    # Find a state not in possible_states
                    non_possible_states = [s for s in self.all_states if s not in possible_states]
                    if non_possible_states:
                        for non_possible in non_possible_states[:2]:  # Add a few constraints
                            constraints.append(semantics.possible(non_possible))
                    
                    # Force main world to be different
                    constraints.append(self.main_point["world"] != z3_model.eval(self.main_point["world"], model_completion=True))
            
            # 3. Force different part-whole relationships
            # This is more involved because it requires bit vectors
            # Choose a few example states to flip part-of relationships
            if len(possible_states) >= 2:
                for i, s1 in enumerate(possible_states[:3]):
                    for j, s2 in enumerate(possible_states[:3]):
                        if i != j:
                            # Get current part-of status
                            try:
                                is_part_val = bool(z3_model.eval(semantics.is_part_of(s1, s2), model_completion=True))
                                # Flip it
                                if is_part_val:
                                    constraints.append(z3.Not(semantics.is_part_of(s1, s2)))
                                else:
                                    constraints.append(semantics.is_part_of(s1, s2))
                            except z3.Z3Exception:
                                pass
                                
        except Exception as e:
            # Log to debug stream instead of printing to user
            import logging
            logger = logging.getLogger(__name__)
            logger.debug(f"Error generating structural constraints: {e}")
            
        return constraints
        
    def get_stronger_constraints(self, z3_model, escape_attempt):
        """Generate stronger constraints for escaping isomorphic models.
        
        This method creates more aggressive constraints when multiple
        isomorphic models have been found in a row. It attempts to create
        constraints that force drastically different models.
        
        Args:
            z3_model: The isomorphic Z3 model to differ from
            escape_attempt: Current escape attempt number (used to escalate constraint strength)
            
        Returns:
            list: List of Z3 constraints for escaping isomorphic models
        """
        constraints = []
        
        try:
            semantics = self.semantics
            
            # 1. Force drastically different world and state counts
            possible_states = self.z3_possible_states or []
            world_states = self.z3_world_states or []
            
            # Count expressions for worlds and possible states
            possible_count_expr = z3.IntVal(0)
            for state in self.all_states:
                possible_count_expr = z3.If(semantics.possible(state), possible_count_expr + 1, possible_count_expr)
                
            world_count_expr = z3.IntVal(0)
            for state in self.all_states:
                world_count_expr = z3.If(semantics.is_world(state), world_count_expr + 1, world_count_expr)
            
            # Force very different counts based on escape attempt
            if escape_attempt == 1:
                # First attempt: try doubling or halving
                constraints.append(possible_count_expr >= len(possible_states) * 2)
                constraints.append(possible_count_expr <= max(1, len(possible_states) // 2))
                constraints.append(world_count_expr >= len(world_states) * 2)
                constraints.append(world_count_expr <= max(1, len(world_states) // 2))
            else:
                # Later attempts: try more extreme values
                constraints.append(world_count_expr == 1)  # Try single world
                constraints.append(world_count_expr == len(self.all_states))  # Try max worlds
                
                # Try to make all states possible or none except minimal required
                constraints.append(possible_count_expr == len(self.all_states))
                min_states = max(1, len(world_states))
                constraints.append(possible_count_expr == min_states)
            
            # 2. Force radically different verification/falsification patterns
            atoms = [syntactic.AtomVal(i) for i in range(3)]
            
            # Create constraints based on escape attempt level
            for atom in atoms:
                # Try to make all states verify or falsify this atom
                all_verify = []
                all_falsify = []
                
                for state in possible_states:
                    all_verify.append(semantics.verify(state, atom))
                    all_falsify.append(semantics.falsify(state, atom))
                
                if escape_attempt == 1:
                    # First attempt: flip all verification/falsification
                    for state in possible_states[:min(5, len(possible_states))]:
                        try:
                            verifies = bool(z3_model.eval(semantics.verify(state, atom), model_completion=True))
                            falsifies = bool(z3_model.eval(semantics.falsify(state, atom), model_completion=True))
                            
                            if verifies:
                                constraints.append(z3.Not(semantics.verify(state, atom)))
                            else:
                                constraints.append(semantics.verify(state, atom))
                                
                            if falsifies:
                                constraints.append(z3.Not(semantics.falsify(state, atom)))
                            else:
                                constraints.append(semantics.falsify(state, atom))
                        except z3.Z3Exception:
                            pass
                else:
                    # Later attempts: try extreme patterns
                    if all_verify:
                        constraints.append(z3.And(all_verify))  # All states verify
                        constraints.append(z3.Not(z3.Or(all_verify)))  # No states verify
                        
                    if all_falsify:
                        constraints.append(z3.And(all_falsify))  # All states falsify
                        constraints.append(z3.Not(z3.Or(all_falsify)))  # No states falsify
                  
            # 3. Force different main world
            if len(world_states) > 1:
                current_main = z3_model.eval(self.main_point["world"], model_completion=True)
                for world in world_states:
                    if world != current_main:
                        constraints.append(self.main_point["world"] == world)
                        break
                        
        except Exception as e:
            # Log to debug stream instead of printing to user
            import logging
            logger = logging.getLogger(__name__)
            logger.debug(f"Error generating stronger constraints: {e}")
            
        return constraints

    def _update_model_structure(self, new_model, previous_structure=None):
        """Update the model structure with a new Z3 model and compute differences.
        
        Args:
            new_model: The new Z3 model to use
            previous_structure: The previous model structure to compare with (optional)
        """
        # Update core model references
        self.z3_model = new_model
        self.z3_model_status = True
        
        # Update derived properties based on the new model
        if self.z3_model is not None:
            self.z3_main_world = self.z3_model[self.main_world]
            self.main_point["world"] = self.z3_main_world
            self.z3_possible_states = [
                bit
                for bit in self.all_states
                if bool(self.z3_model.evaluate(self.semantics.possible(bit)))
            ]
            self.z3_world_states = [
                bit
                for bit in self.z3_possible_states
                if bool(self.z3_model.evaluate(self.semantics.is_world(bit)))
            ]
        
        # Calculate and store differences if we have a previous structure
        if previous_structure is not None:
            self.model_differences = self._compute_model_differences(previous_structure)
            self.previous_model = previous_structure
    
    def _compute_model_differences(self, previous_structure):
        """Compute differences between this model structure and the previous one.
        
        Args:
            previous_structure: The previous model structure to compare with
            
        Returns:
            dict: Structured differences between the models
        """
        differences = {
            'sentence_letters': {},
            'semantic_functions': {},
            'model_structure': {}
        }
        
        # Compare sentence letter valuations
        for letter in self.model_constraints.sentence_letters:
            current_verifiers, current_falsifiers = self._get_verifier_falsifier_states(letter)
            prev_verifiers, prev_falsifiers = previous_structure._get_verifier_falsifier_states(letter)
            
            if current_verifiers != prev_verifiers or current_falsifiers != prev_falsifiers:
                differences['sentence_letters'][letter] = {
                    'old': (prev_verifiers, prev_falsifiers),
                    'new': (current_verifiers, current_falsifiers)
                }
        
        # Compare semantic function interpretations for relations like 'R' if available
        semantics = self.semantics
        prev_semantics = previous_structure.semantics
        
        for attr_name in dir(semantics):
            if attr_name.startswith('_'):
                continue
                
            attr = getattr(semantics, attr_name)
            if not isinstance(attr, z3.FuncDeclRef):
                continue
                
            # Get domain size
            arity = attr.arity()
            if arity == 0:
                continue
            
            # For unary and binary functions, check specific values
            if arity <= 2:
                # Get the domain size (number of worlds)
                n_worlds = len(self.z3_world_states)
                
                # Create constraints for all relevant inputs
                func_diffs = {}
                for inputs in self._generate_input_combinations(arity, n_worlds):
                    try:
                        # Check values in both models
                        args = [z3.IntVal(i) for i in inputs]
                        curr_value = self.z3_model.eval(attr(*args), model_completion=True)
                        prev_value = previous_structure.z3_model.eval(attr(*args), model_completion=True)
                        
                        # Store if different
                        if str(curr_value) != str(prev_value): 
                            func_diffs[inputs] = {
                                'old': prev_value,
                                'new': curr_value
                            }
                    except z3.Z3Exception:
                        pass
                
                if func_diffs:
                    differences['semantic_functions'][attr_name] = func_diffs
        
        # Compare model structure components
        current_world_count = len(self.z3_world_states)
        prev_world_count = len(previous_structure.z3_world_states)
        
        if current_world_count != prev_world_count:
            differences['model_structure']['world_count'] = {
                'old': prev_world_count,
                'new': current_world_count
            }
        
        # Check if there are any differences
        if (not differences['sentence_letters'] and 
            not differences['semantic_functions'] and 
            not differences['model_structure']):
            return None
        
        return differences
    
    def _generate_input_combinations(self, arity, domain_size):
        """Generate all relevant input combinations for a function of given arity.
        
        Args:
            arity: Number of arguments the function takes
            domain_size: Size of the domain (typically number of worlds)
            
        Returns:
            list: All relevant input combinations
        """
        import itertools
        # For n-ary functions, generate all combinations of inputs
        # from the domain, which is typically the world indices
        domain = range(domain_size)
        return itertools.product(domain, repeat=arity)

    # TODO: remove?
    def save_to(self, example_name, theory_name, include_constraints, output):
        """Save the model details to a file.
        
        Writes a complete representation of the model to the specified file, including
        evaluation results, state space, and optionally the model constraints.
        
        Args:
            example_name (str): Name of the example being evaluated
            theory_name (str): Name of the logical theory being used
            include_constraints (bool): Whether to include model constraints in output
            output (TextIO): File object to write the model details to
        """
        constraints = self.model_constraints.all_constraints
        self.print_all(example_name, theory_name, output)
        
        # Include model differences in the output file if they exist and this isn't a stopped model
        if (not hasattr(self, '_is_stopped_model') or not self._is_stopped_model) and \
           hasattr(self, 'model_differences') and self.model_differences:
            self.print_model_differences(output)
            
        self.build_test_file(output)
        if include_constraints:
            print("# Satisfiable constraints", file=output)
            print(f"all_constraints = {constraints}", file=output)
