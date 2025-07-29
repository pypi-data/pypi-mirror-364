import matplotlib.pyplot as plt

def line_plot(data, title="Line Plot"):
    plt.figure(figsize=(8, 4))
    plt.plot(data, marker='o')
    plt.title(title)
    plt.xlabel("Index")
    plt.ylabel("Value")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# from my_plot_package import line_plot
# line_plot([1, 2, 3, 4, 5], title="Test Plot")
