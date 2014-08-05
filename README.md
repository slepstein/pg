## pg: Python Graphics Framework

pg is a lightweight OpenGL graphics framework for Python.

It is a work in progress.

### Sample

    import pg

    class Window(pg.Window):
        def __init__(self):
            super(Window, self).__init__((640, 480), 'Hello World')
        def setup(self):
            self.program = pg.Program(
                'shaders/vertex.glsl', 'shaders/fragment.glsl')
            self.context = pg.Context(self.program)
            self.context.position = pg.VertexBuffer(3, [
                -1, -1, 0,
                1, -1, 0,
                0, 1, 0,
            ])
        def update(self, t, dt):
            matrix = pg.Matrix()
            matrix = matrix.rotate((0, 1, 0), t)
            matrix = matrix.translate((0, 0, -4))
            matrix = matrix.perspective(65, 1.333, 0.1, 100)
            self.context.matrix = matrix
        def draw(self):
            self.clear()
            self.context.draw(pg.GL_TRIANGLES)
        def teardown(self):
            pass

    if __name__ == "__main__":
        app = pg.App()
        Window()
        app.run()

### Dependencies

    brew install glfw3
    pip install PyOpenGL glfw