from customtkinter import CTk, CTkCanvas

class App(CTk):
    def __init__(self):
        super().__init__()
        self.title("Ball Animation Example")
        self.geometry("400x300")

        # Create a canvas widget
        self.canvas = CTkCanvas(self, width=400, height=300)
        self.canvas.pack()

        # Define start and end points
        self.x1, self.y1 = 50, 50
        self.x2, self.y2 = 350, 250
        self.ball_radius = 10
        self.canvas.create_line(self.x1, self.y1, self.x2, self.y2, width=3, fill="blue")


        # Create a red ball at the start point
        self.ball = self.canvas.create_oval(
            self.x1 - self.ball_radius, self.y1 - self.ball_radius,
            self.x1 + self.ball_radius, self.y1 + self.ball_radius,
            fill="red", outline="red"
        )

        # Initialize animation parameters
        self.dx = (self.x2 - self.x1) / 100  # Change in x per step
        self.dy = (self.y2 - self.y1) / 100  # Change in y per step
        self.steps = 100  # Total number of steps

        # Start the animation
        self.animate_ball()

    def animate_ball(self):
        # Update the ball's position
        self.canvas.move(self.ball, self.dx, self.dy)

        # Decrement steps and continue animation if steps remain
        self.steps -= 1
        if self.steps > 0:
            self.after(5, self.animate_ball)  # Update every 5ms
        else:
            self.canvas.move(self.ball, self.x1 - self.x2, self.y1 - self.y2)
            self.steps = 1000
            self.after(5, self.animate_ball)

app = App()
app.mainloop()
