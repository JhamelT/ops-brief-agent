output "lambda_name" {
  value = aws_lambda_function.agent.function_name
}

output "table_name" {
  value = aws_dynamodb_table.runs.name
}