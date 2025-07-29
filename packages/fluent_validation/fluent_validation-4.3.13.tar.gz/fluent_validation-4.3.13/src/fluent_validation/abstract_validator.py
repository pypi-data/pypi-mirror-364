from __future__ import annotations
from typing import Awaitable, Callable, Optional, Type, overload, override, TYPE_CHECKING
import re

from fluent_validation.internal.CollectionPropertyRule import CollectionPropertyRule
from fluent_validation.internal.ExtensionInternal import ExtensionsInternal
# from fluent_validation.syntax import IRuleBuilderInitialCollection

if TYPE_CHECKING:
    from fluent_validation.IValidationRuleInternal import IValidationRuleInternal
    from fluent_validation.internal.ValidationStrategy import ValidationStrategy
    from .syntax import IConditionBuilder, IRuleBuilder
    from fluent_validation.IValidationRule import IValidationRule
    from fluent_validation.DefaultValidatorOptions import IRuleBuilderInitial

from fluent_validation.ValidationException import ValidationException
from fluent_validation.internal.TrackingCollection import TrackingCollection
from fluent_validation.IValidator import IValidator
from fluent_validation.results.ValidationResult import ValidationResult
from fluent_validation.IValidationContext import IValidationContext, ValidationContext
from fluent_validation.internal.PropertyRule import PropertyRule
from fluent_validation.internal.RuleBuilder import RuleBuilder
from fluent_validation.internal.RuleSetValidatorSelector import RulesetValidatorSelector

from fluent_validation.ValidatorOptions import ValidatorOptions
from fluent_validation.enums import CascadeMode
from fluent_validation.internal.IncludeRule import IncludeRule
from fluent_validation.internal.ConditionBuilder import ConditionBuilder


class AbstractValidator[T](IValidator[T]):
    # region constructor
    def __init__(self, type_model: Type[T]) -> None:
        self._type_model: Type[T] = type_model
        self._classLevelCascadeMode: Callable[[], CascadeMode] = lambda: ValidatorOptions.Global.DefaultClassLevelCascadeMode
        self._ruleLevelCascadeMode: Callable[[], CascadeMode] = lambda: ValidatorOptions.Global.DefaultRuleLevelCascadeMode
        self._rules: TrackingCollection[IValidationRuleInternal] = TrackingCollection()

    @property
    def CascadeMode(self) -> CascadeMode:
        if self.ClassLevelCascadeMode == self.RuleLevelCascadeMode:
            return self.ClassLevelCascadeMode
        elif self.ClassLevelCascadeMode == CascadeMode.Continue and self.RuleLevelCascadeMode == CascadeMode.Stop:
            return CascadeMode.Stop  # COMMENT: Original is CascadeMode.StopOnFirstFailure
        else:
            raise Exception(
                "There is no conversion to a single CascadeMode value from the current combination of "
                + "ClassLevelCascadeMode and RuleLevelCascadeMode. "
                + "Please use these properties instead of the deprecated CascadeMode going forward."
            )

    @CascadeMode.setter
    def CascadeMode(self, value: CascadeMode):
        self.ClassLevelCascadeMode = value
        self.RuleLevelCascadeMode = value

    def __getitem__(self, _index: int):
        return self._rules.__getitem__(_index)

    # endregion

    @overload
    def validate(self, instance: T) -> ValidationResult: ...

    @overload
    def validate(self, instance: IValidationContext) -> ValidationResult: ...

    @overload
    def validate(self, instance: T, options: Callable[[ValidationStrategy[T]], None]) -> ValidationResult: ...

    @override
    def validate(self, instance: T | IValidationContext, options: Optional[Callable[[ValidationStrategy[T]], None]] = None) -> ValidationResult:
        if options:
            return self.validate(ValidationContext[T].CreateWithOptions(instance, options))

        if not options and isinstance(instance, IValidationContext):
            # instance acts as context, because it does not exists override operator as C#, I need to call context attr as instance
            return self.__validate__(ValidationContext[T].GetFromNonGenericContext(instance))

        if not options and type(instance) is ValidationContext:
            return self.__validate__(instance)

        return self.__validate__(ValidationContext[T](instance, None, ValidatorOptions.Global.ValidatorSelectors.DefaultValidatorSelectorFactory()))

    def __validate__(self, context: ValidationContext[T]) -> ValidationResult:
        # Use synchronous validation to avoid async deadlocks in nested collections
        return self.ValidateSync(context)

    @overload
    async def ValidateAsync(self, instance: IValidationContext) -> Awaitable[ValidationResult]: ...
    @overload
    async def ValidateAsync(self, instance: T) -> Awaitable[ValidationResult]: ...

    @override
    async def ValidateAsync(self, instance):
        if isinstance(instance, IValidationContext):
            return await self.__validate_async__(ValidationContext[T].GetFromNonGenericContext(instance))

        return await self.__validate_async__(ValidationContext[T](instance, None, ValidatorOptions.Global.ValidatorSelectors.DefaultValidatorSelectorFactory()))

    async def __validate_async__(self, instance: ValidationContext[T]):
        instance.IsAsync = True
        return await self.ValidateInternalAsync(instance, useAsync=True)

    async def ValidateInternalAsync(self, context: ValidationContext[T], useAsync: bool) -> ValidationResult:
        result: ValidationResult = ValidationResult(errors=context.Failures)
        shouldContinue: bool = self.pre_validate(context, result)

        if not shouldContinue:
            if not result.is_valid and context.ThrowOnFailures:
                self.RaiseValidationException(context, result)

            return result

        count: int = len(self._rules)
        for i in range(count):
            totalFailures = len(context.Failures)
            await self._rules[i].ValidateAsync(context, useAsync)

            if self.ClassLevelCascadeMode == CascadeMode.Stop and len(result.errors) > totalFailures:
                break

        self.SetExecutedRuleSets(result, context)

        if not result.is_valid and context.ThrowOnFailures:
            self.RaiseValidationException(context, result)
        return result

        # COMMENT: used in private async ValueTask<ValidationResult> ValidateInternalAsync(ValidationContext<T> context, bool useAsync, CancellationToken cancellation) {...}

    @overload
    def ValidateSync(self, instance: IValidationContext) -> ValidationResult: ...
    @overload
    def ValidateSync(self, instance: T) -> ValidationResult: ...

    @override
    def ValidateSync(self, instance):
        if isinstance(instance, IValidationContext):
            return self.__validate_sync__(ValidationContext[T].GetFromNonGenericContext(instance))

        return self.__validate_sync__(ValidationContext[T](instance, None, ValidatorOptions.Global.ValidatorSelectors.DefaultValidatorSelectorFactory()))

    def __validate_sync__(self, instance: ValidationContext[T]):
        instance.IsAsync = False
        return self.ValidateInternalSync(instance)

    def ValidateInternalSync(self, context: ValidationContext[T]) -> ValidationResult:
        """Synchronous version of ValidateInternalAsync to avoid event loop deadlocks in nested validations."""
        result: ValidationResult = ValidationResult(errors=context.Failures)
        shouldContinue: bool = self.pre_validate(context, result)

        if not shouldContinue:
            if not result.is_valid and context.ThrowOnFailures:
                self.RaiseValidationException(context, result)
            return result

        count: int = len(self._rules)
        for i in range(count):
            totalFailures = len(context.Failures)
            # COMMENT: Call synchronous validation instead of async
            self._rules[i].ValidateSync(context)

            if self.ClassLevelCascadeMode == CascadeMode.Stop and len(result.errors) > totalFailures:
                break

        self.SetExecutedRuleSets(result, context)

        if not result.is_valid and context.ThrowOnFailures:
            self.RaiseValidationException(context, result)
        return result

    def SetExecutedRuleSets(self, result: ValidationResult, context: ValidationContext[T]) -> None:
        obj = context.RootContextData.get("_FV_RuleSetsExecuted", None)
        if obj is not None and isinstance(obj, set):
            result.RuleSetsExecuted = list(obj)
        else:
            result.RuleSetsExecuted = RulesetValidatorSelector.DefaultRuleSetNameInArray
        return None

    # public virtual IValidatorDescriptor CreateDescriptor() => new ValidatorDescriptor<T>(Rules)

    def CanValidateInstancesOfType(self, _type: Type) -> bool:
        return issubclass(_type, self.__orig_bases__[0].__args__[0])

    def rule_for[TProperty](self, expression: Callable[[T], TProperty]) -> IRuleBuilderInitial[T, TProperty]:
        ExtensionsInternal.Guard(expression, "Cannot pass None to rule_for", "expression")
        rule: PropertyRule[T, TProperty] = PropertyRule[T, TProperty].create(expression, lambda: self.RuleLevelCascadeMode, self._type_model)
        self._rules.append(rule)
        self.OnRuleAdded(rule)
        return RuleBuilder[T, TProperty](rule, self)

    #   public IRuleBuilderInitial<T, TTransformed> Transform<TProperty, TTransformed>(Expression<Func<T, TProperty>> from, Func<TProperty, TTransformed> to) {
    #         from.Guard("Cannot pass null to Transform", nameof(from))
    #         rule = PropertyRule<T, TTransformed>.Create(lambda: to,() => RuleLevelCascadeMode)
    #         Rules.Add(rule)
    #         OnRuleAdded(rule)
    #         return new RuleBuilder<T, TTransformed>(rule, this)
    #     }

    #     public IRuleBuilderInitial<T, TTransformed> Transform<TProperty, TTransformed>(Expression<Func<T, TProperty>> from, Func<T, TProperty, TTransformed> to) {
    #         from.Guard("Cannot pass null to Transform", nameof(from))
    #         rule = PropertyRule<T, TTransformed>.Create(lambda: to,() => RuleLevelCascadeMode)
    #         Rules.Add(rule)
    #         OnRuleAdded(rule)
    #         return new RuleBuilder<T, TTransformed>(rule, this)
    #     }

    def rule_for_each[TElement](self, expression: Callable[[T], list[TElement]]) -> IRuleBuilder[T, TElement]:  # IRuleBuilderInitialCollection[T, TElement]:
        ExtensionsInternal.Guard(expression, "Cannot pass null to rule_for_each", "expression")
        rule = CollectionPropertyRule[T, TElement].Create(expression, lambda: self.RuleLevelCascadeMode, self._type_model)
        self._rules.append(rule)
        self.OnRuleAdded(rule)
        return RuleBuilder[T, TElement](rule, self)

    #     public IRuleBuilderInitialCollection<T, TTransformed> TransformForEach<TElement, TTransformed>(Expression<Func<T, IEnumerable[TElement]>> expression, Func<TElement, TTransformed> to) {
    #         expression.Guard("Cannot pass null to rule_for_each", nameof(expression))
    #         rule = CollectionPropertyRule<T, TTransformed>.CreateTransformed(lambda: to,() => RuleLevelCascadeMode)
    #         Rules.Add(rule)
    #         OnRuleAdded(rule)
    #         return new RuleBuilder<T, TTransformed>(rule, this)
    #     }

    #     public IRuleBuilderInitialCollection<T, TTransformed> TransformForEach<TElement, TTransformed>(Expression<Func<T, IEnumerable[TElement]>> expression, Func<T, TElement, TTransformed> to) {
    #         expression.Guard("Cannot pass null to rule_for_each", nameof(expression))
    #         rule = CollectionPropertyRule<T, TTransformed>.CreateTransformed(lambda: to,() => RuleLevelCascadeMode)
    #         Rules.Add(rule)
    #         OnRuleAdded(rule)
    #         return new RuleBuilder<T, TTransformed>(rule, this)
    #     }

    # FIXME [x]: It's wrong implementation
    def rule_set(self, rule_set_name: str, action: Callable[[], None]) -> None:
        rule_set_names = [name.strip() for name in re.split(r"[,;]", rule_set_name)]
        with self._rules.OnItemAdded(lambda r: setattr(r, "RuleSets", rule_set_names)):
            action()
        return None

    @override
    def when(self, predicate: Callable[[T], bool], action: Callable[..., None]) -> IConditionBuilder:
        """
        Defines a condition that applies to several rules

        Attributes
        -
        - predicate: The condition that should apply to multiple rules
        - action: Action that encapsulates the rules.

        """
        return self.__When(lambda x, _: predicate(x), action)

    def __When(self, predicate: Callable[[T, ValidationContext[T]], bool], action: Callable[..., None]) -> IConditionBuilder:
        return ConditionBuilder[T](self.Rules).when(predicate, action)

    @override
    def unless(self, predicate: Callable[[T], bool], action: Callable[..., None]) -> IConditionBuilder:
        return self.__Unless(lambda x, _: predicate(x), action)

    def __Unless(self, predicate: Callable[[T, ValidationContext[T]], bool], action: Callable[..., None]) -> IConditionBuilder:
        return ConditionBuilder[T](self.Rules).unless(predicate, action)

    # def WhenAsync(Func<T, CancellationToken, Task<bool>> predicate, Action action)->IConditionBuilder:
    #     return WhenAsync((x, _, cancel) => predicate(x, cancel), action)

    # def WhenAsync(Func<T, ValidationContext<T>, CancellationToken, Task<bool>> predicate, Action action)->IConditionBuilder:
    #     return new AsyncConditionBuilder<T>(Rules).WhenAsync(predicate, action)

    # def UnlessAsync(Func<T, CancellationToken, Task<bool>> predicate, Action action)->IConditionBuilder:
    #     return UnlessAsync((x, _, cancel) => predicate(x, cancel), action)

    # def UnlessAsync(Func<T, ValidationContext<T>, CancellationToken, Task<bool>> predicate, Action action)->IConditionBuilder:
    #     return new AsyncConditionBuilder<T>(Rules).UnlessAsync(predicate, action)

    @overload
    def include(self, rulesToInclude: IValidator[T]) -> None: ...
    @overload
    def include[TValidator: IValidator[T]](self, rulesToInclude: Callable[[T], TValidator]): ...

    def include[TValidator: IValidator[T]](self, rulesToInclude: IValidator[T] | Callable[[T], TValidator]):
        rule = IncludeRule[T].Create(rulesToInclude, lambda: self.RuleLevelCascadeMode)
        self.Rules.append(rule)
        self.OnRuleAdded(rule)

    def pre_validate(self, context: ValidationContext[T], result: ValidationResult) -> bool:
        return True

    def RaiseValidationException(self, context: ValidationContext[T], result: ValidationResult) -> None:
        raise ValidationException(errors=result.errors)

    def OnRuleAdded(self, rule: IValidationRule[T]) -> None:
        return None

    # region Properties
    @property
    def Rules(self) -> TrackingCollection[IValidationRuleInternal[T]]:
        return self._rules

    @property
    def ClassLevelCascadeMode(self) -> CascadeMode:
        return self._classLevelCascadeMode()

    @ClassLevelCascadeMode.setter
    def ClassLevelCascadeMode(self, value):
        self._classLevelCascadeMode = lambda: value

    @property
    def RuleLevelCascadeMode(self) -> CascadeMode:
        return self._ruleLevelCascadeMode()

    @RuleLevelCascadeMode.setter
    def RuleLevelCascadeMode(self, value):
        self._ruleLevelCascadeMode = lambda: value

    # endregion
