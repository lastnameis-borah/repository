#### DRAIN VOLTAGE = 11V ####
#### CURRENT = 4A ####

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import numpy as np
import matplotlib.pyplot as plt

def Gate_Voltage(given_current):
    # Assuming x_values and y_values are your lists of x and y values respectively
    x1_values = [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6, 6.5, 7, 7.5, 8, 8.5, 9]    # Gate voltage values
    y1_values = [3.914, 3.500, 3.013, 2.525, 2.036, 1.546, 1.056, 0.564, 0.073, -0.433, -0.942, -1.450, -1.957, -2.464, -2.968, -3.471, -3.880, -3.830, -3.821]     # Current values

    # Convert lists to numpy arrays
    x_values = np.array(x1_values).reshape(-1, 1)
    y_values = np.array(y1_values)

    # Split the data into training and testing sets
    x_train, x_test, y_train, y_test = train_test_split(x_values, y_values, test_size=0.2, random_state=42)

    # Initialize the Linear Regression model
    model = LinearRegression()

    # Train the model
    model.fit(y_train.reshape(-1, 1), x_train)  # Reshape y_train to a 2D array

    # Use the trained model to predict x values given y values
    predicted_x = model.predict(y_test.reshape(-1, 1))  # Reshape y_test to a 2D array for prediction

    # Model Evaluation
    score = model.score(y_test.reshape(-1, 1), x_test)  # Reshape y_test to a 2D array for evaluation
    # print("Model Score:", score)

    # Model prediction
    # given_current = 2.5 # Current value against which voltage needs to be predicted
    predicted_voltage_value = model.predict(np.array([[given_current]]).reshape(-1, 1))  # Reshape given_y to a 2D array
    return predicted_voltage_value

gate_voltage = float(input("Current required across the coils: "))

print(f"Gate Voltage to be provided: {Gate_Voltage(gate_voltage)[0][0]:.2f}V")

# # Plot the values
# plt.plot(x1_values, y1_values)

# # Plot the original data
# plt.scatter(x_values, y_values, color='blue', label='Original Data')

# plt.xlabel('Gate Voltage (in V)')
# plt.ylabel('Current (in A)')
# plt.title('Original data vs Predicted data')
# # plt.legend()
# plt.grid(True)
# plt.show()