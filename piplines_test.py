from json_pipeline import JsonPipeline
import os
import json
def json_pipiline_test():
    k = 5
    num_generate = 4
    curr_generate = 0
    
    def dummy_generate_func(promt):
        nonlocal curr_generate
        if num_generate * k == curr_generate:
           curr_generate += 1
           raise Exception("Were stop here")
        curr_generate += 1
        return f"dummy response {curr_generate}"
    input_path = "test_data.json"
    output_path = "test_output.json"

    #create json dummy data 
    dummy_data = [{"question":f"dummy question {i}"} for i in range(10)]
    # create a new json file nad insert the dummy data
    with open(input_path, 'w') as f:
        json.dump(dummy_data, f, indent=4)
    # create output file path
    try:
        json_pipeline = JsonPipeline(
            generate_func=dummy_generate_func,
            k=k,
            data_path=input_path,
            out_path=output_path
        )
        try:
            json_pipeline.evaluate()
        except Exception as e:
            print(f"Caught exception as expected: {e}")
            if e.args[0] != "Were stop here":
                print("Test failed: Unexpected exception message.")
                raise e
        #check output file has 4 entries
        with open(output_path, 'r') as f:
            output_data = json.load(f)
        assert len(output_data) == num_generate, f"Expected {num_generate} entries, got {len(output_data)}"
        print("Test passed: Output file has correct number of entries.")
        #create a new pipeline instance to test recovery
        json_pipeline_recovery = JsonPipeline(
            generate_func=dummy_generate_func,
            k=k,
            data_path=input_path,
            out_path=output_path
        )
        #continue evaluation
        json_pipeline_recovery.evaluate()
        #check output file has 10 entries
        with open(output_path, 'r') as f:
            output_data = json.load(f)
        assert len(output_data) == 10, f"Expected 10 entries after recovery, got {len(output_data)}"
        print("Test passed: Recovery works correctly, output file has correct number of entries after resuming.")
    except Exception as e:
        print(f"Test failed with exception: {e}")
        raise e
    finally:    
        #cleanup
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)
if __name__ == "__main__":
    json_pipiline_test()
    print("All tests passed.")
    