import pytest
from src.lambda_function import transform_csv

def test_transform_csv():
    input_data = """name,age\nAlice,30\nBob,25"""
    output_data = transform_csv(input_data)
    lines = output_data.strip().split("\n")

    # Check headers
    assert lines[0] == "name,age,Processed"
    # Check data    pip install pytest
    assert lines[1] == "Alice,30,Yes"
    assert lines[2] == "Bob,25,Yes"