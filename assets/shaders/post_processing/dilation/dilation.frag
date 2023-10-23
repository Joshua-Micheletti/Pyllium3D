#version 330 core

in vec2 frag_uv;
// in float frag_param_0;
// in float frag_param_1;

uniform sampler2D screen_texture;

out vec4 frag_color;

void main() {
    int size = int(1);
    float separation = 0.7;
    float min_threshold = 0.1;
    float max_threshold = 0.5;

    vec2 tex_size = textureSize(screen_texture, 0);

    vec4 tex_color = texture(screen_texture, frag_uv);

    float mx = 0.0;
    vec4 cmx = tex_color;

    for (int i = -size; i <= size; ++i) {
        for (int j = -size; j <= size; ++j) {
            // For a rectangular shape.
            // if (false);

            // For a diamond shape;
            if (!(abs(i) <= size - abs(j))) { continue; }

            // For a circular shape.
            // if (!(distance(vec2(i, j), vec2(0, 0)) <= size)) {
            //     continue;
            // }

            vec4 c = texture(screen_texture, (frag_uv + (vec2(i, j) * separation) / tex_size));

            float mxt = dot(c.rgb, vec3(0.21, 0.72, 0.07));

            if (mxt > mx) {
                mx  = mxt;
                cmx = c;
            }
        }
    }

    tex_color.rgb = mix(tex_color.rgb, cmx.rgb, smoothstep(min_threshold, max_threshold, mx));

    frag_color = vec4(tex_color.rgb, 1.0);
    // frag_color = cmx;
    // frag_color = vec4(gl_FragCoord);
}