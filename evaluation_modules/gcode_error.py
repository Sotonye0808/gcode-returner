import numpy as np

def execution_error(expected_toolpath, actual_toolpath):
    try:
        if expected_toolpath is None or actual_toolpath is None:
            raise ValueError("Both toolpaths must be provided")

        # Convert inputs to numpy arrays if they aren't already
        expected = np.array(expected_toolpath)
        actual = np.array(actual_toolpath)

        # Verify dimensions match
        if expected.shape != actual.shape:
            raise ValueError("Toolpath dimensions must match")

        # Compute Euclidean distance error
        errors = np.linalg.norm(expected - actual, axis=1)
        mean_error = np.mean(errors)

        return mean_error, errors

    except Exception as e:
        print(f"Error calculating execution error: {str(e)}")
        return None, None

# Experimental usage
if __name__ == "__main__":
    # Example expected G-code toolpath
    expected = np.array([
        [10, 20], [15, 25], [20, 30], [25, 35], [30, 40]
    ])

    # Example actual robot movement log
    actual = np.array([
        [10, 21], [14, 26], [19, 31], [26, 34], [31, 41]
    ])

    mean_error, errors = execution_error(expected, actual)
    
    if mean_error is not None:
        print(f"Mean Execution Error: {mean_error:.2f} units")
        print(f"Error at each point: {errors}")