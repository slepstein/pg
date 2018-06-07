from .core import Program
from .matrix import Matrix
from .util import normalize

class BaseProgram(Program):
    def __init__(self):
        super(BaseProgram, self).__init__(self.VS, self.FS)

class SolidColorProgram(BaseProgram):
    '''Renders all primitives with a single, solid color.

    :param matrix: the model-view-projection matrix, required
    :param position: vertex buffer containing vertex positions, required
    :param color: the color to use (default: white)
    '''
    VS = '''
    #version 120

    uniform mat4 matrix;

    attribute vec4 position;

    void main() {
        gl_Position = matrix * position;
    }
    '''
    FS = '''
    #version 120

    uniform vec4 color;

    void main() {
        gl_FragColor = color;
    }
    '''
    def set_defaults(self, context):
        context.color = (1.0, 1.0, 1.0, 1.0)

class TextureProgram(BaseProgram):
    '''Renders with a texture and no lighting.

    :param matrix: the model-view-projection matrix, required
    :param position: vertex buffer containing vertex positions, required
    :param sampler: texture to use, required
    '''
    VS = '''
    #version 120

    uniform mat4 matrix;

    attribute vec4 position;
    attribute vec2 uv;

    varying vec2 frag_uv;

    void main() {
        gl_Position = matrix * position;
        frag_uv = uv;
    }
    '''
    FS = '''
    #version 120

    uniform sampler2D sampler;

    varying vec2 frag_uv;

    void main() {
        vec4 color = texture2D(sampler, frag_uv);
        if (color.a == 0) {
            discard;
        }
        gl_FragColor = color;
    }
    '''
    def set_defaults(self, context):
        pass


class DirectionalLightProgram(BaseProgram):
    '''Renders the scene with a single, directional light source. Optionally,
        primitives can be textured or independently colored.
        
        :param matrix: the model-view-projection matrix, required
        :param model_matrix: the model matrix, required
        :param position: vertex buffer containing vertex positions, required
        :param normal: vertex buffer containing vertex normals, required
        :param uv: vertex buffer containing vertex texture coordinates, required if use_texture == True
        :param color: vertex buffer containing vertex colors, required if use_color == True
        :param sampler: texture to use, required if use_texture == True
        :param camera_position: the camera position in model space, required
        :param normal_matrix: the normal matrix, transposed inverse of model matrix, required
        :param light_direction: vector specifying light direction, default: (1, 1, 1) normalized
        :param object_color: color for all vertices if textures and color attributes are disabled, default: (0.4, 0.6, 0.8)
        :param ambient_color: ambient light color, default: (0.3, 0.3, 0.3)
        :param light_color: directional light color, default: (0.7, 0.7, 0.7)
        :param specular_power: controls exponent used in specular lighting, default: 32.0
        :param specular_multiplier: controls intensity of specular lighting, default: 1.0
        :param use_texture: controls whether a texture is to be used, default: False
        :param use_color: controls whether per-vertex colors are provided, default: False
        '''
    VS = '''
        #version 120
        
        uniform mat4 matrix;
        uniform mat4 model_matrix;
        uniform mat4 normal_matrix;
        
        attribute vec4 position;
        attribute vec3 normal;
        attribute vec2 uv;
        attribute vec3 color;
        
        varying vec3 frag_position;
        varying vec3 frag_normal;
        varying vec2 frag_uv;
        varying vec3 frag_color;
        
        void main() {
        gl_Position = matrix * position;
        frag_position = vec3(model_matrix * position);
        frag_normal = mat3(normal_matrix) * normal;
        frag_uv = uv;
        frag_color = color;
        }
        '''
    FS = '''
        #version 120
        
        uniform sampler2D sampler;
        uniform vec3 camera_position;
        
        uniform vec3 light_direction;
        uniform vec3 object_color;
        uniform vec3 ambient_color;
        uniform vec3 light_color;
        uniform float specular_power;
        uniform float specular_multiplier;
        uniform bool use_texture;
        uniform bool use_color;
        
        varying vec3 frag_position;
        varying vec3 frag_normal;
        varying vec2 frag_uv;
        varying vec3 frag_color;
        
        void main() {
        vec3 color = object_color;
        if (use_color) {
        color = frag_color;
        }
        if (use_texture) {
        color = vec3(texture2D(sampler, frag_uv));
        }
        float diffuse = max(dot(frag_normal, light_direction), 0.0);
        float specular = 0.0;
        if (diffuse > 0.0) {
        vec3 camera_vector = normalize(camera_position - frag_position);
        specular = pow(max(dot(camera_vector,
        reflect(-light_direction, frag_normal)), 0.0), specular_power);
        }
        vec3 light = ambient_color + light_color * diffuse +
        specular * specular_multiplier;
        gl_FragColor = vec4(min(color * light, vec3(1.0)), 1.0);
        }
        '''
    def set_defaults(self, context):
        context.model_matrix = Matrix()
        context.normal_matrix = Matrix().inverse().transpose()
        context.light_direction = normalize((1, 1, 1))
        context.object_color = (0.4, 0.6, 0.8)
        context.ambient_color = (0.3, 0.3, 0.3)
        context.light_color = (0.7, 0.7, 0.7)
        context.specular_power = 32.0
        context.specular_multiplier = 1.0
        context.use_texture = False
        context.use_color = False


class DirectionalLightWithTextureAtlasProgram(BaseProgram):
    '''Renders the scene with a single, directional light source. Optionally,
        primitives can be textured or independently colored.
        
        :param matrix: the model-view-projection matrix, required
        :param model_matrix: the model matrix, required
        :param position: vertex buffer containing vertex positions, required
        :param normal: vertex buffer containing vertex normals, required
        :param uv: vertex buffer containing vertex texture coordinates, required if use_texture == True
        :param color: vertex buffer containing vertex colors, required if use_color == True
        :param sampler: texture to use, required if use_texture == True
        :param camera_position: the camera position in model space, required
        :param normal_matrix: the normal matrix, transposed inverse of model matrix, required
        :param light_direction: vector specifying light direction, default: (1, 1, 1) normalized
        :param object_color: color for all vertices if textures and color attributes are disabled, default: (0.4, 0.6, 0.8)
        :param ambient_color: ambient light color, default: (0.3, 0.3, 0.3)
        :param light_color: directional light color, default: (0.7, 0.7, 0.7)
        :param specular_power: controls exponent used in specular lighting, default: 32.0
        :param specular_multiplier: controls intensity of specular lighting, default: 1.0
        :param tile_offset: texture atlas tile offset: (0.0,0.0)
        :param tile_ratio: texture atlas tile ratio: (1.0/9.0,1.0/9.0)
        :param tile_repeat: texture atlas tile repeat: (1.0,1.0)
        :param use_wrap: controls whether a tile is texture wrapped: False
        :param use_tile: controls whether a tile is to be used, default: False
        :param use_texture: controls whether a texture is to be used, default: False
        :param use_color: controls whether per-vertex colors are provided, default: False
        '''
    VS = '''
        #version 120
        
        uniform mat4 matrix;
        uniform mat4 model_matrix;
        uniform mat4 normal_matrix;
        
        attribute vec4 position;
        attribute vec3 normal;
        attribute vec2 uv;
        attribute vec3 color;
        
        varying vec3 unfrag_position;
        varying vec3 unfrag_normal;
        varying vec3 frag_position;
        varying vec3 frag_normal;
        varying vec2 frag_uv;
        varying vec3 frag_color;
        
        void main() {
        gl_Position = matrix * position;
        unfrag_position = vec3(position);
        unfrag_normal = vec3(normal);
        frag_position = vec3(model_matrix * position);
        frag_normal = mat3(normal_matrix) * normal;
        frag_uv = uv;
        frag_color = color;
        }
        '''
    FS = '''
        #version 120
        
        uniform sampler2D sampler;
        uniform vec3 camera_position;
        
        uniform vec3 light_direction;
        uniform vec3 object_color;
        uniform vec3 ambient_color;
        uniform vec3 light_color;
        uniform float specular_power;
        uniform float specular_multiplier;
        uniform bool use_texture;
        uniform bool use_tile;
        uniform bool use_wrap;
        uniform bool use_color;
        uniform vec2 tile_ratio;
        uniform vec2 tile_offset;
        uniform vec2 tile_repeat;
        
        varying vec3 unfrag_position;
        varying vec3 unfrag_normal;
        varying vec3 frag_position;
        varying vec3 frag_normal;
        varying vec2 frag_uv;
        varying vec3 frag_color;
        
        void main() {
        vec3 color = object_color;
        if (use_color) {
            color = frag_color;
        }
        if (use_texture) {
            vec2 texCoord = frag_uv;
            if (use_tile) {
                vec2 tile_uv = frag_uv;
                if (use_wrap) {
                    tile_uv = vec2(dot(unfrag_normal.zxy, unfrag_position), dot(unfrag_normal.yzx, unfrag_position));
                    
                    //tile_uv = vec2(dot(unfrag_normal.zyx, unfrag_position), dot(unfrag_normal.yzx, unfrag_position));
                    //tile_uv = vec2(dot(unfrag_normal.zyx, unfrag_position), dot(unfrag_normal.yxz, unfrag_position));
                    //tile_uv = vec2(dot(unfrag_normal.zyx, unfrag_position), dot(unfrag_normal.xyz, unfrag_position));

                    //tile_uv = vec2(dot(unfrag_normal.zxy, unfrag_position), dot(unfrag_normal.yxz, unfrag_position));
                    //tile_uv = vec2(dot(unfrag_normal.zxy, unfrag_position), dot(unfrag_normal.xyz, unfrag_position));
                    //tile_uv = vec2(dot(unfrag_normal.zxy, unfrag_position), dot(unfrag_normal.xzy, unfrag_position));
                    texCoord = tile_offset + tile_ratio * fract(tile_uv/tile_repeat);
                }
                else {
                    texCoord = tile_offset + tile_ratio * fract(tile_uv*tile_repeat);
                }
            }
            color = vec3(texture2D(sampler, texCoord));
        }
        float diffuse = max(dot(frag_normal, light_direction), 0.0);
        float specular = 0.0;
        if (diffuse > 0.0) {
        vec3 camera_vector = normalize(camera_position - frag_position);
        specular = pow(max(dot(camera_vector,
        reflect(-light_direction, frag_normal)), 0.0), specular_power);
        }
        vec3 light = ambient_color + light_color * diffuse +
        specular * specular_multiplier;
        gl_FragColor = vec4(min(color * light, vec3(1.0)), 1.0);
        }
        '''
    def set_defaults(self, context):
        context.model_matrix = Matrix()
        context.normal_matrix = Matrix().inverse().transpose()
        context.light_direction = normalize((1, 1, 1))
        context.object_color = (0.4, 0.6, 0.8)
        context.ambient_color = (0.3, 0.3, 0.3)
        context.light_color = (0.7, 0.7, 0.7)
        context.specular_power = 32.0
        context.specular_multiplier = 1.0
        context.use_color = False
        context.use_texture = False
        context.use_tile = False
        context.use_wrap = False
        context.tile_size = (1.0/9.0,1.0/9.0)
        context.tile_offset = (0.0,0.0)


# TODO: same as TextureProgram? consolidate?
class TextProgram(BaseProgram):
    '''Renders 2D text using a font texture. Used by the built-in ``pg.Font``.

    :param matrix: the model-view-projection matrix, required
    :param position: vertex buffer containing vertex positions, required
    :param uv: vertex buffer containing vertex texture coordinates, required
    :param sampler: font texture to use, required
    '''
    VS = '''
    #version 120

    uniform mat4 matrix;

    attribute vec4 position;
    attribute vec2 uv;

    varying vec2 frag_uv;

    void main() {
        gl_Position = matrix * position;
        frag_uv = uv;
    }
    '''
    FS = '''
    #version 120

    uniform sampler2D sampler;

    varying vec2 frag_uv;

    void main() {
        vec4 color = texture2D(sampler, frag_uv);
        if (color.a == 0) {
            discard;
        }
        gl_FragColor = color;
    }
    '''
    def set_defaults(self, context):
        pass
