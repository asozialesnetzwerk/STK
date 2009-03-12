unit agfx_types;

interface

uses SysUtils;

const
     LOG_ERR  = 0;
     LOG_MSG  = 1;
     LOG_WARN  = 2;

const
    _GIS_INACTIVE   = 0;
    _GIS_ACTIVE     = 1;
    _GIS_NORMAL     = 2;
    _GIS_OVER       = 3;
    _GIS_PRESSED    = 4;
    _GIS_ENABLE     = 5;
    _GIS_DISABLE    = 6;

const
    WHITE           : array[0..3] of Single = (1, 1, 1, 1);
    BLACK           : array[0..3] of Single = (0, 0, 0, 1);

// PREDEFINED TEXTURE UNIT LAYER DEFINITION
const
    TU_DECAL_MAP    = 0;
    TU_BUMP_MAP     = 1;
    TU_GLOSS_MAP    = 2;
    TU_SHADOW_MAP   = 3;
    TU_SPOTLIGHT_MAP = 3;

const

    F3D_EPSILON     = 0.0000001;
    _X              = 0;
    _Y              = 1;
    _Z              = 2;

    _R              = 0;
    _G              = 1;
    _B              = 2;
    _A              = 3;

const

    CAMERA_TYPE_FPS = 0;
    CAMERA_TYPE_TARGET = 1;
    CAMERA_TYPE_ORBIT = 2;

    CAMERA_MODE_WALK = 0;
    CAMERA_MODE_FLY = 1;

type
    TF3D_AxisEnum = (AXIS_X, AXIS_Y, AXIS_Z);

type
    TF3DMaterialType = (MT_COLOR, MT_TEXTURE, MT_SHADER, MT_FX);

type
    TF3D_EngineMode = (EM_RENDER, EM_EDIT);

type
    TF3D_FACE_FLAG = (FACE_RENDER, FACE_FX);

type
    TF3D_BillboardMode = (BM_AXIS_X, BM_AXIS_Y, BM_AXIS_Z, BM_DIRECTIONAL, BM_SPRITE);



////{******************************************************************************}
////{ 2D vector
////{******************************************************************************}


type
    TF3D_Vector2f = record
        case boolean of
            TRUE: (X, Y: single);
            False: (V: array[0..1] of single);
    end;
    pTF3D_Vector2f = ^TF3D_Vector2f;

type
    TF3D_Vector2i = record
        case boolean of
            TRUE: (X, Y: integer);
            False: (V: array[0..1] of integer);
    end;
    pTF3D_Vector2i = ^TF3D_Vector2i;

////{******************************************************************************}
////{ 3D vector
////{******************************************************************************}

type
    TF3D_Vector3f = record
        case boolean of
            TRUE: (X, Y, Z: single);
            False: (V: array[0..2] of single);
    end;
    pTF3D_Vector3f = ^TF3D_Vector3f;

type
    TF3D_Vector3i = record
        case boolean of
            TRUE: (X, Y, Z: integer);
            False: (V: array[0..2] of integer);
    end;
    pTF3D_Vector3i = ^TF3D_Vector3i;

type
    TF3D_Triangle = record
        A, B, C: INTEGER;
    end;

type
    TF3D_VertexTBN = packed record
        s, t: Single;
        Normal: TF3D_Vector3f;
        sTangent: TF3D_Vector3f;
        tTangent: TF3D_Vector3f;                                                // Also called BiNormal
    end;
////{******************************************************************************}
////{ 4D vector
////{******************************************************************************}

type
    TF3D_Vector4f = record
        case boolean of
            TRUE: (X, Y, Z, W: single);
            False: (V: array[0..3] of single);
    end;
    pTF3D_Vector4f = ^TF3D_Vector4f;


type
    TF3D_Vector4i = record
        case boolean of
            TRUE: (X, Y, Z, W: single);
            False: (V: array[0..3] of single);
    end;
    pTF3D_Vector4i = ^TF3D_Vector4i;

////{******************************************************************************}
////{ RGB COLOR - float
////{******************************************************************************}

type
    TF3D_COLOR3f = record
        case boolean of
            true: (R, G, B: single);
            false: (c: array[0..2] of single);
    end;
    pTF3D_COLOR3f = ^TF3D_COLOR3f;


type TF3D_Matrix4f = array[0..3, 0..3] of Single;
type TF3D_Matrix4d = array[0..3, 0..3] of Double;
type TF3D_Matrix4i = array[0..3, 0..3] of Integer;

////{******************************************************************************}
////{ RGB COLOR - integer
////{******************************************************************************}
type
    TF3D_COLOR3i = record
        case boolean of
            true: (R, G, B: integer);
            false: (c: array[0..2] of integer);
    end;
////{******************************************************************************}
////{ RGBA COLOR
////{******************************************************************************}
type
    TF3D_COLOR4f = record
        case boolean of
            true: (R, G, B, A: single);
            false: (c: array[0..3] of single);
    end;
    pTF3D_COLOR4f = ^TF3D_COLOR4f;
//{******************************************************************************}
//{ RGBA COLOR - integer
//{******************************************************************************}
type
    TF3D_COLOR4i = record
        case boolean of
            true: (R, G, B, A: integer);
            false: (c: array[0..3] of integer);
    end;
    pTF3D_COLOR4i = ^TF3D_COLOR4i;

//{******************************************************************************}
//{ RGBA COLOR
//{******************************************************************************}
type
    TF3D_COLOR4b = record
        case boolean of
            true: (R, G, B, A: byte);
            false: (c: array[0..3] of byte);
    end;
    pTF3D_COLOR4b = ^TF3D_COLOR4b;

//{******************************************************************************}
//{ FACE
//{******************************************************************************}

type
    TF3D_Face = record
        Flag: TF3D_FACE_FLAG;
        indices: array [0..3] of integer;
        IndicesCount: integer;
        material_name: string[128];
        material_id: integer;
        normal:TF3D_Vector3f;
    end;

    pTF3D_FACE = ^TF3D_FACE;

//{******************************************************************************}
//{ VERTEX BUFFER
//{******************************************************************************}

type
    TF3D_VertexBuffer = record
        vertex: array of TF3D_Vector3f;
        uv: array of TF3D_Vector2f;
        //sTangent: array of TF3D_Vector3f;
        //tTangent: array of TF3D_Vector3f;
        Normal: array of TF3D_Vector3f;
        color: array of TF3D_Color4f;
    end;

type
    TF3D_TextureUnit = record
        texture_name: string[128];
        texture_file: string[255];
        id: integer;
        used: boolean;
        bEvent: boolean;
        event_name: string[128];
        event_id: integer;
    end;

//{******************************************************************************}
//{ MATERIAL
//{******************************************************************************}

type
    TF3D_Material = record
        name: string;
        typ: TF3DMaterialType;
        color: TF3D_COLOR4f;
        vertex_color: boolean;
        //diffuse: TF3D_COLOR4f;
        Specular: TF3D_COLOR4f;
        Ambient: TF3D_COLOR4f;
        Shinises: single;
        texture_unit: array[0..3] of TF3D_TextureUnit;
        // shader
        shader_name: string;
        bShader: boolean;
        shader_id: integer;
        // bPrelighting
        HW_lighting: boolean;                                                   // if true then color will be used as material for HW GL LIGHTING
        bAlphaTest:boolean;
        bDepthTest:Boolean;
        bFaceCulling:Boolean;


    end;

type
    TF3D_LightType = (LT_SPOT, LT_POINT, LT_DIRECTIONAL);

type
  // Light source attributes:
    TF3D_LightSource = record
    // light type
        _type: TF3D_LightType;
    // Position.
        Position: TF3D_Vector3f;
    // Colors (I'll disregard emission for now).
        Ambient: TF3D_Color4f;
        Diffuse: TF3D_Color4f;
        Specular: TF3D_Color4f;
    // spot
        spot_cut_off: integer;
        spot_target: TF3D_Vector3f;
        spot_direction: TF3D_Vector3f;
        spot_exponent: single;

        spot_constant_att: single;
        spot_linear_att: single;
        spot_quadratic_att: single;
    // Constant attenuation factor.
        Attenuation: Single;
        glow_sprite: string;
        glow_sprite_id:integer;

        range: single;
        enable: boolean;
    end;


//{******************************************************************************}
//{ PLANE Ax+By+Cz+D=0;  Normal[A,B,C] D=distance
//{******************************************************************************}
type
    TF3D_PLANE = record
        normal: TF3D_Vector3f;
        dist: single;
    end;
    pTF3D_PLANE = ^TF3D_PLANE;

//{******************************************************************************}
//{ TRANSFORM
//{******************************************************************************}
type
    TF3D_TRANSFORMATION = record
        position: TF3D_Vector3f;
        rotation: TF3D_Vector3f;
        scale: TF3D_Vector3f;
    end;

//{******************************************************************************}
//{ TEXTURE SOURCE
//{******************************************************************************}

type
    TF3D_TEXTURE = record
        name: string[64];
        width, height: cardinal;
        color_depth: integer;
        data: cardinal;
    end;
    pTF3D_TEXTURE = ^TF3D_TEXTURE;

//{******************************************************************************}
//{ MATRIX 4x4
//{******************************************************************************}
type
    pTF3D_MATRIX = ^TF3D_MATRIX;
    TF3D_MATRIX = array[0..3, 0..3] of single;

type
    TF3D_Feature = (
        SV_PINF,                                                                // Infinite projection matrix.
        SV_ZFAIL,                                                               // ZFail shadows ("Carmack's reverse").
        SV_STENCIL_WRAP,                                                        // Stencil value wrapping.
        SV_TWO_SIDED_STENCIL,                                                   // Two-sided stencil testing.
        SV_SCISSOR_RECT,                                                        // Scissor testing for light bounds.
        SV_DEPTH_BOUNDS,                                                        // Depth testing for light bounds.
        SV_DEPTH_CLAMP,                                                         // Z value clamping.
        SV_EXTERNAL_TRIANGLES                                                   // External triangles (negative W value).
        );
    TF3D_FeatureSet = set of TF3D_Feature;

//{******************************************************************************}
//{ GUI helpers
//{******************************************************************************}

type
    TF3D_DrawSkinHelper = record
        _pos: array[0..2, 0..2] of TF3D_Vector2f;
        _size: array[0..2, 0..2] of TF3D_Vector2f;
    end;

type
    pBoolean = ^Boolean;

type
    TGUI_ITEM_STATUS = (GIS_ACTIVE, GIS_INACTIVE, GIS_NORMAL, GIS_OVER, GIS_PRESSED);

//{******************************************************************************}
//{ HELPERS
//{******************************************************************************}

type
    TF3D_Axis3f = record
        _forward: TF3D_Vector3f;
        _right: TF3D_Vector3f;
        _up: TF3D_Vector3f;
    end;

function SetColor4f(r, g, b, a: single): TF3D_COlor4f;
function SetColor3f(r, g, b: single): TF3D_COlor3f;
function SetColor3i(r, g, b: integer): TF3D_COlor3i;
function SetColor4i(r, g, b, a: integer): TF3D_COlor4i;
function SetVector3f(x, y, z: single): TF3D_Vector3f;
function SetVector4f(x, y, z: single; w: Single = 1): TF3D_Vector4f;
function SetVector2f(x, y: single): TF3D_Vector2f;

function ReadParam(var Text: string): string;

function StrToCount(str: string): integer;

function StrToV3f(str: string): TF3D_Vector3f;
function StrToV2f(str: string): TF3D_Vector2f;
function StrToV3i(str: string): TF3D_Vector3i;
function StrToC3f(str: string): TF3D_Color3f;
function StrToBoolean(str: string): Boolean;

function Color4fToSTr(sep: string; val: TF3D_Color4f): string;
function Vector3fToStr(sep: string; val: TF3D_Vector3f): string;
function Vector4fToStr(sep: string; val: TF3D_Vector4f): string;


const
    F3D_ORIGIN2     : TF3D_Vector2f = (x: 0; y: 0);
    F3D_X_AXIS2     : TF3D_Vector2f = (x: 1; y: 0);
    F3D_Y_AXIS2     : TF3D_Vector2f = (x: 0; y: 1);
    F3D_Z_AXIS2     : TF3D_Vector2f = (x: 0; y: 0);

    F3D_ORIGIN3     : TF3D_Vector3f = (x: 0; y: 0; z: 0);
    F3D_X_AXIS3     : TF3D_Vector3f = (x: 1; y: 0; z: 0);
    F3D_Y_AXIS3     : TF3D_Vector3f = (x: 0; y: 1; z: 0);
    F3D_Z_AXIS3     : TF3D_Vector3f = (x: 0; y: 0; z: 1);

    F3D_ORIGIN4     : TF3D_Vector4f = (x: 0; y: 0; z: 0; w: 1);
    F3D_X_AXIS4     : TF3D_Vector4f = (x: 1; y: 0; z: 0; w: 1);
    F3D_Y_AXIS4     : TF3D_Vector4f = (x: 0; y: 1; z: 0; w: 1);
    F3D_Z_AXIS4     : TF3D_Vector4f = (x: 0; y: 0; z: 1; w: 1);

var
    EXE_PATH        : string;

implementation

//------------------------------------------------------------------------------

function ReadParam(var Text: string): string;
var
    Start           : Integer;
begin
    Text := Trim(Text);
    Start := Pos(';', Text);

    if (Start <> 0) then begin
        Result := Copy(Text, 1, Start - 1);
        Delete(Text, 1, Start);
    end else begin
        Result := Text;
        Text := '';
    end;
    Result := Trim(Result);
end;

function SetColor4f(r, g, b, a: single): TF3D_COlor4f;
begin
    result.r := r;
    result.g := g;
    result.b := b;
    result.a := a;
end;

function SetColor3f(r, g, b: single): TF3D_COlor3f;
begin
    result.r := r;
    result.g := g;
    result.b := b;

end;

function SetColor3i(r, g, b: integer): TF3D_COlor3i;
begin
    result.r := r;
    result.g := g;
    result.b := b;

end;

function SetColor4i(r, g, b, a: integer): TF3D_COlor4i;
begin
    result.r := r;
    result.g := g;
    result.b := b;
    result.a := a;
end;

function SetVector3f(x, y, z: single): TF3D_Vector3f;
begin
    result.x := x;
    result.y := y;
    result.z := z;

end;

function SetVector4f(x, y, z: single; w: Single = 1): TF3D_Vector4f;
begin
    result.x := x;
    result.y := y;
    result.z := z;

end;

function SetVector2f(x, y: single): TF3D_Vector2f;
begin
    result.x := x;
    result.y := y;
end;

function StrToV2f(str: string): TF3D_Vector2f;
begin
    result.X := StrToFloatDef(ReadParam(str), 0);
    result.Y := StrToFloatDef(ReadParam(str), 0);

end;

function StrToV3f(str: string): TF3D_Vector3f;
begin
    result.X := StrToFloatDef(ReadParam(str), 0);
    result.Y := StrToFloatDef(ReadParam(str), 0);
    result.Z := StrToFloatDef(ReadParam(str), 0);
end;

function StrToV3i(str: string): TF3D_Vector3i;
begin
    StrToV3i.X := StrToIntDef(ReadParam(str), 0);
    StrToV3i.Y := StrToIntDef(ReadParam(str), 0);
    StrToV3i.Z := StrToIntDef(ReadParam(str), 0);
end;

function StrToC3f(str: string): TF3D_Color3f;
begin
    StrToC3f.R := StrToFloatDef(ReadParam(str), 0);
    StrToC3f.G := StrToFloatDef(ReadParam(str), 0);
    StrToC3f.B := StrToFloatDef(ReadParam(str), 0);
end;

function StrToBoolean(str: string): Boolean;
begin
    if UPPERCASE(str) = 'TRUE' then StrToBoolean := true else StrToBoolean := false;
end;

function StrToCount(str: string): integer;
var
    a               : integer;
    item            : string;
begin
    a := 0;
    item := 'null';
    while item <> '' do
    begin
        item := ReadParam(str);
        Inc(a);
    end;

    result := a - 1;
end;

function Color4fToSTr(sep: string; val: TF3D_Color4f): string;
begin
    result := FloatToStr(val.R) + sep + FloatToStr(val.G) + sep + FloatToStr(val.B) + sep + FloatToStr(val.A);
end;

function Vector3fToStr(sep: string; val: TF3D_Vector3f): string;
begin
    result := FloatToStr(val.X) + sep + FloatToStr(val.Y) + sep + FloatToStr(val.Z);
end;

function Vector4fToStr(sep: string; val: TF3D_Vector4f): string;
begin
    result := FloatToStr(val.X) + sep + FloatToStr(val.Y) + sep + FloatToStr(val.Z)+ sep + FloatToStr(val.W);
end;

end.

