package domain

import (
	"fmt"
	"testing"
)

const positiveExampleSection = `### Example Set 1: Positive Example (Category: Business Logic)

[Assertion]
"The {OrderProcessor} service uses the {BusinessRulesEngine} to validate and apply business rules for all incoming orders, ensuring that orders comply with the company's policies."

[Code]
{OrderProcessor}:
` + "```" + `python
class OrderProcessor:
	def __init__(self, business_rules_engine):
		self.business_rules_engine = business_rules_engine

	def process_order(self, order):
		if self.business_rules_engine.apply_rules(order):
			# Process the order
			print("Order processed successfully.")
		else:
			print("Order failed validation. Cannot proceed.")
` + "```" + `

{BusinessRulesEngine}:
` + "```" + `python
class BusinessRulesEngine:
	def __init__(self):
		self.rules = [
			self.check_order_value,
			self.check_customer_credit,
			# Add more rules here
		]

	def apply_rules(self, order):
		for rule in self.rules:
			if not rule(order):
				return False
		return True

	def check_order_value(self, order):
		# Example rule: Orders must be over $100
		return order.total >= 100

	def check_customer_credit(self, order):
		# Example rule: Customer must have sufficient credit
		return order.customer_credit >= order.total
` + "```" + `

[Thinking]
- The assertion states that the OrderProcessor uses the BusinessRulesEngine to validate orders against business rules.
- Looking at the OrderProcessor class, it does indeed use the BusinessRulesEngine to check orders before processing them.
- The BusinessRulesEngine applies a series of predefined rules to the order, such as checking the order value and customer credit.
- If all rules pass, the order is processed; otherwise, it's rejected.
- This approach modularizes the business logic, making it easier to manage and update rules without affecting the core OrderProcessor logic.
- The code seems to align well with the assertion, facilitating the application of business rules to order processing.
`

const negativeExampleSection = `### Example Set 2: Negative Example (Category: Business Logic)

[Assertion]
"The {ProductPricingService} always uses the {PricingStrategy} to determine the final price of products, considering discounts, taxes, and other pricing factors."

[Code]
{ProductPricingService}:
` + "```" + `python
class ProductPricingService:
	def calculate_product_price(self, product):
		# Hard-coded pricing logic without using PricingStrategy
		base_price = product.base_price
		discount = 0.1  # Fixed 10% discount
		tax_rate = 0.08  # Fixed 8% tax rate
		final_price = base_price * (1 - discount) * (1 + tax_rate)
		return final_price
` + "```" + `

{PricingStrategy}:
` + "```" + `python
from abc import ABC, abstractmethod

class PricingStrategy(ABC):
	@abstractmethod
	def calculate_price(self, product):
		pass
` + "```" + `

[Thinking]
- The assertion claims that the ProductPricingService uses the PricingStrategy to determine product prices.
- However, the provided ProductPricingService class calculates prices using hard-coded logic.
- It applies a fixed discount and tax rate without referencing or implementing any PricingStrategy.
- This direct approach contradicts the assertion, which expects the use of a pricing strategy for flexibility and maintainability.
- The lack of strategy implementation in the pricing service suggests a potential oversight or misalignment with the expected business logic.

[Explanation]
- The ` + "`" + `ProductPricingService` + "`" + ` does not utilize any ` + "`" + `PricingStrategy` + "`" + ` implementation.
- It instead relies on fixed, hard-coded logic for calculating prices, which does not adhere to the expected use of a pricing strategy.
- Key aspects such as discounts and taxes are not dynamic or configurable through a strategy, limiting the service's ability to adapt to changing business needs.
- The service's design does not align with the assertion's requirement for using a pricing strategy to determine product prices.
`

func Example_parseAssertionText() {
	assertionText, err := parseAssertionText(positiveExampleSection)
	if err != nil {
		panic(err)
	}
	fmt.Println(assertionText)

	// Output:
	// "The {OrderProcessor} service uses the {BusinessRulesEngine} to validate and apply business rules for all incoming orders, ensuring that orders comply with the company's policies."
}

func Example_parseThoughts() {
	thoughts, err := parseThoughts(positiveExampleSection)
	if err != nil {
		panic(err)
	}
	fmt.Println(thoughts)

	// Output:
	// - The assertion states that the OrderProcessor uses the BusinessRulesEngine to validate orders against business rules.
	// - Looking at the OrderProcessor class, it does indeed use the BusinessRulesEngine to check orders before processing them.
	// - The BusinessRulesEngine applies a series of predefined rules to the order, such as checking the order value and customer credit.
	// - If all rules pass, the order is processed; otherwise, it's rejected.
	// - This approach modularizes the business logic, making it easier to manage and update rules without affecting the core OrderProcessor logic.
	// - The code seems to align well with the assertion, facilitating the application of business rules to order processing.
}

func Example_parseCodeSection() {
	codeSection, err := parseCodeSection(positiveExampleSection)
	if err != nil {
		panic(err)
	}
	fmt.Println(codeSection)

	// Output:
	// {OrderProcessor}:
	// ```python
	// class OrderProcessor:
	// 	def __init__(self, business_rules_engine):
	// 		self.business_rules_engine = business_rules_engine
	//
	// 	def process_order(self, order):
	// 		if self.business_rules_engine.apply_rules(order):
	// 			# Process the order
	// 			print("Order processed successfully.")
	// 		else:
	// 			print("Order failed validation. Cannot proceed.")
	// ```
	//
	// {BusinessRulesEngine}:
	// ```python
	// class BusinessRulesEngine:
	// 	def __init__(self):
	// 		self.rules = [
	// 			self.check_order_value,
	// 			self.check_customer_credit,
	// 			# Add more rules here
	// 		]
	//
	// 	def apply_rules(self, order):
	// 		for rule in self.rules:
	// 			if not rule(order):
	// 				return False
	// 		return True
	//
	// 	def check_order_value(self, order):
	// 		# Example rule: Orders must be over $100
	// 		return order.total >= 100
	//
	// 	def check_customer_credit(self, order):
	// 		# Example rule: Customer must have sufficient credit
	// 		return order.customer_credit >= order.total
	// ```
}

func Test_parseExplanation(t *testing.T) {
	explanation := parseExplanation(positiveExampleSection)
	if explanation != nil {
		t.Errorf("Expected explanation to be nil, got: %v", *explanation)
	}
}

func Example_parseExplanation() {
	explanation := parseExplanation(negativeExampleSection)
	fmt.Println(*explanation)

	// Output:
	// - The `ProductPricingService` does not utilize any `PricingStrategy` implementation.
	// - It instead relies on fixed, hard-coded logic for calculating prices, which does not adhere to the expected use of a pricing strategy.
	// - Key aspects such as discounts and taxes are not dynamic or configurable through a strategy, limiting the service's ability to adapt to changing business needs.
	// - The service's design does not align with the assertion's requirement for using a pricing strategy to determine product prices.
}
