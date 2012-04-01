package net.sourceforge.supertuxkart.b3d;

import java.io.File;
import java.io.FileInputStream;
import java.io.InputStream;
import java.util.ArrayList;

public class B3DReader
{

    /*
    byte [] data = new byte[] {1,2,3,4};
    
    ByteBuffer b = ByteBuffer.wrap(data);
    
    System.out.println(b.getInt());
    System.out.println(b.getFloat());
     */
    
    
    static Chunk curr_node = null;
    static ArrayList<Chunk> m_all_nodes = new ArrayList<Chunk>();
    static ArrayList<Chunk> m_all_texs = new ArrayList<Chunk>();
    static ArrayList<Chunk> m_all_brus = new ArrayList<Chunk>();

    static boolean showVrts = true;
    static boolean showKeyframes = true;
    
    public static int readInt(InputStream i) throws Exception
    {
        byte[] bytes = new byte[4];
        if (i.read(bytes) != 4)
        {
            throw new RuntimeException("Can't read int");
        }
        
        int as_int = ((bytes[0] & 0xFF) | ((bytes[1] & 0xFF) << 8) | ((bytes[2] & 0xFF) << 16) | ((bytes[3] & 0xFF) << 24));
        if (as_int == -0) as_int = 0;
        return as_int;
    }
    
    public static String readString(InputStream i) throws Exception
    {
        String out = "";
        
        int b;
        
        while ((b = i.read()) != 0)
        {
            out += (char)b;
        }
        
        return out;
    }
    
    public static float readFloat(InputStream i) throws Exception
    {
        byte[] bytes = new byte[4];
        if (i.read(bytes) != 4)
        {
            throw new RuntimeException("Can't read int");
        }
        
        int packed_bytes = ((bytes[0] & 0xFF) | ((bytes[1] & 0xFF) << 8) | ((bytes[2] & 0xFF) << 16) | ((bytes[3] & 0xFF) << 24));
        
        float f = Float.intBitsToFloat(packed_bytes);
        if (f == -0) f = 0;
        return f;
    }
    
    public static String readFloat(InputStream i, boolean printBytes) throws Exception
    {
        byte[] bytes = new byte[4];
        if (i.read(bytes) != 4)
        {
            throw new RuntimeException("Can't read int");
        }
        
        int packed_bytes = ((bytes[0] & 0xFF) | ((bytes[1] & 0xFF) << 8) | ((bytes[2] & 0xFF) << 16) | ((bytes[3] & 0xFF) << 24));
        
        float f = Float.intBitsToFloat(packed_bytes);
        if (f == -0) f = 0;
        return f + ""; // + " [" + Integer.toHexString(packed_bytes) + "]";
    }
    
    public static void readBB3DChunk(InputStream i, final int length) throws Exception
    {
        int version = readInt(i);
        System.out.println("    Version: " + version);
        
        while (i.available() > 0) {
            readChunk(i, 1);
        }
    }
    
    public static String format3(float f)
    {
        String lOut = String.format("%.3f", f);
        
        if (lOut.equals("-0.000")) return "0.000";
        
        return lOut;
    }
    
    public static String format2(float f)
    {
        return String.format("%.2f", f);
    }
    
    public static void readTEXSChunk(InputStream i, final int length) throws Exception
    {
        int read = 0;
        
        int n = 0;
        
        while (read < length)
        {
            String filename = readString(i);
            read += filename.length() + 1;
            int flags = readInt(i);
            int blend = readInt(i);
            float x = readFloat(i);
            float y = readFloat(i);
            float x_scale = readFloat(i);
            float y_scale = readFloat(i);
            float rot = readFloat(i);
            read += 28;
            
            System.out.println("        TEXS entry " + n + ": ");
            System.out.println("            Filename: " + filename);
            System.out.println("            Flags: " + flags);
            System.out.println("            Blend: " + blend);
            System.out.println("            Position: (" + format2(x) + ", " + format2(y)  + ")");
            System.out.println("            Scale: (" + format2(x_scale) + ", " + format2(y_scale) + ")");
            System.out.println("            Rotation: " + rot);
            
            n++;
        }
    }
    
    public static void readBRUSChunk(InputStream i, final int length) throws Exception
    {
        int num = readInt(i);
        int read = 4;
        
        int brush_id = 0;
        
        while (read < length)
        {
            String name = readString(i);
            read += name.length() + 1;
            
            float r = readFloat(i);
            float g = readFloat(i);
            float b = readFloat(i);
            float a = readFloat(i);
            float shininess = readFloat(i);
            int blend = readInt(i);
            int fx = readInt(i);
            read += 28;

            System.out.println("        BRUSH " + brush_id + " :");
            System.out.println("            Material name: " + name);
            System.out.println("            RGBA: (" + r + ", " + g + ", " + b + ", " + a + ")");
            System.out.println("            Shininess: " + shininess);
            System.out.println("            Blend: " + blend);
            System.out.println("            FX: " + fx);
            
            
            for (int n=0; n<num; n++)
            {
                int tid = readInt(i);
                read += 4;
                System.out.println("            TextureID[" + n + "] : " + tid);
            }
            
            brush_id++;
        }
    }
    
    public static void readVRTSChunk(InputStream i, final int length) throws Exception
    {
        int flags = readInt(i);
        int tex_coord_sets = readInt(i);
        int tex_coord_set_size = readInt(i);
        
        System.out.println("            Flags: " + flags + " (Normals=" + ((flags & 0x1) != 0) + ", VertexColors=" + ((flags & 0x2) != 0) + ")");
        System.out.println("            Texture coords per vertex: " + tex_coord_sets);
        System.out.println("            Tex_coord_set_size: " + tex_coord_set_size);
        
        int read = 12;
        
        while (read < length)
        {
            float x = readFloat(i);
            float y = readFloat(i);
            float z = readFloat(i);
            read += 12;
            
            if (showVrts)
                System.out.println("            Vertex: (" + format2(x) + ", " + format2(y) + ", " + format2(z) + ")");
            
            if ((flags & 0x1) != 0)
            {
                float nx = readFloat(i);
                float ny = readFloat(i);
                float nz = readFloat(i);
                read += 12;
                
                if (showVrts)
                    System.out.println("            Normal: (" + format2(nx) + ", " + format2(ny) + ", " + format2(nz) + ")");
            }
            
            if ((flags & 0x2) != 0)
            {
                float r = readFloat(i);
                float g = readFloat(i);
                float b = readFloat(i);
                float a = readFloat(i);
                read += 16;
                
                if (showVrts)
                    System.out.println("            RGBA: (" + r + ", " + g + ", " + b + ", " + a + ")");
            }
            
            for (int n=0; n<tex_coord_sets; n++)
            {
                String coords = "";
                for (int m=0; m<tex_coord_set_size; m++)
                {
                    float coord = readFloat(i);
                    coords += coord + " ";
                    read += 4;
                }
                
                if (showVrts)
                    System.out.println("            TexCoord: ( " + coords + ")");
            }
        }
    }
    
    public static void readTRISChunk(InputStream i, final int length) throws Exception
    {
        int brush_id = readInt(i);
        System.out.println("            Tris.BrushID: " + brush_id);
        
        int read = 4;
        
        while (read < length)
        {
            int vertex_1 = readInt(i);
            int vertex_2 = readInt(i);
            int vertex_3 = readInt(i);
            read += 12;
            if (showVrts)
                System.out.println("            Triangle: (" + vertex_1 + ", " + vertex_2 + ", " + vertex_3 + ")");
        }
    }
    
    public static void readMESHChunk(InputStream i, final int length) throws Exception
    {
        int brush_id = readInt(i);
        System.out.println("        BrushID: " + brush_id);
        
        // VRTS chunk
        readChunk(i, 2);
        
        // TRIS chunks
        readChunk(i, 2);
    }
    
    public static void readBONEChunk(InputStream i, final int length) throws Exception
    {
        int read = 0;
        
        while (read < length)
        {
            int vertex_id = readInt(i);
            float weigth = readFloat(i);
            read += 8;
            
            if (showVrts)
                System.out.println("        Vertex: " + vertex_id + " (weight=" + weigth + ")");
        }
    }
    
    public static void readKEYSChunk(InputStream i, final int length) throws Exception
    {
        int flags = readInt(i);
        System.out.println("        Flags: (Pos=" + ((flags & 0x1) != 0) + ", scale=" + ((flags & 0x2) != 0) + ", rot=" + ((flags & 0x4) != 0) + ")");

        int read = 4;
        
        while (read < length)
        {
            int frame = readInt(i);
            read += 4;
            
            if (showKeyframes)
                System.out.println("        Frame: " + frame);
            
            if ((flags & 0x1) != 0)
            {
                float x = readFloat(i);
                float y = readFloat(i);
                float z = readFloat(i);
                read += 12;
                
                if (showKeyframes)
                    System.out.println("            Position: (" + format2(x) + ", " + format2(y) + ", " + format2(z) + ")");
            }
            if ((flags & 0x2) != 0)
            {
                float x = readFloat(i);
                float y = readFloat(i);
                float z = readFloat(i);
                read += 12;
                
                if (showKeyframes)
                    System.out.println("            Scale: (" + format2(x) + ", " + format2(y) + ", " + format2(z) + ")");
            }
            if ((flags & 0x4) != 0)
            {
                float w = readFloat(i);
                float x = readFloat(i);
                float y = readFloat(i);
                float z = readFloat(i);
                read += 16;
                
                if (showKeyframes)
                    System.out.println("            Rot: (" + format3(w)  + ", " + format3(x) + ", " + format3(y) + ", " + format3(z) + ")");
            }
        }
    }
    
    public static void readANIMChunk(InputStream i, final int length) throws Exception
    {
        int flags = readInt(i);
        int frames = readInt(i);
        float fps = readFloat(i);
        System.out.println("        Flags: " + flags + "(unused)");
        System.out.println("        Frames: " + frames);
        System.out.println("        FPS: " + fps);
    }
    
    static class Chunk
    {
        ArrayList<String> m_strings = new ArrayList<String>();
        ArrayList<Chunk> m_children = new ArrayList<Chunk>();
        String name;
        String m_type;
        
        public Chunk(String type)
        {
            m_type = type;
        }
        public void add(String s) { m_strings.add(s); }
    }
    
    public static void readNODEChunk(InputStream i, final int length) throws Exception
    {
        Chunk node = new Chunk("NODE");
        curr_node = node;
        m_all_nodes.add(node);
        
        node.name = readString(i);
        float x = readFloat(i);
        float y = readFloat(i);
        float z = readFloat(i);
        float x_scale = readFloat(i);
        float y_scale = readFloat(i);
        float z_scale = readFloat(i);
        float w_rot = readFloat(i);
        float x_rot = readFloat(i);
        float y_rot = readFloat(i);
        float z_rot = readFloat(i);
        
        System.out.println("        Name: " + node.name);
        System.out.println("        Position: (" + format2(x) + ", " + format2(y) + ", " + format2(z) + ")");
        System.out.println("        Scale: (" + format2(x_scale) + ", " + format2(y_scale) + ", " + format2(z_scale) + ")");
        System.out.println("        Rotation: (" + format3(w_rot) + ", " + format3(x_rot) + ", " + format3(y_rot) + ", " + format3(z_rot) + ")");
    }
    
    public static void readChunk(InputStream i, int level) throws Exception
    {
        byte[] tag = new byte[4];
        if (i.read(tag) != 4)
        {
            throw new RuntimeException("Can't read chunk tag");
        }
        String tag_str = "" + (char)tag[0] + "" + (char)tag[1] + "" + (char)tag[2] + "" + (char)tag[3];
        
        int len = readInt(i);
        
        for (int n=0; n<level; n++) System.out.print("    ");
        // System.out.println(tag_str + " (" + len + " bytes)");
        System.out.println(tag_str);
        
        if (tag_str.equals("BB3D"))
        {
            readBB3DChunk(i, len);
        }
        else if (tag_str.equals("TEXS"))
        {
            readTEXSChunk(i, len);
        }
        else if (tag_str.equals("BRUS"))
        {
            readBRUSChunk(i, len);
        }
        else if (tag_str.equals("VRTS"))
        {
            readVRTSChunk(i, len);
        }
        else if (tag_str.equals("TRIS"))
        {
            readTRISChunk(i, len);
        }
        else if (tag_str.equals("MESH"))
        {
            readMESHChunk(i, len);
        }
        else if (tag_str.equals("BONE"))
        {
            readBONEChunk(i, len);
        }
        else if (tag_str.equals("KEYS"))
        {
            readKEYSChunk(i, len);
        }
        else if (tag_str.equals("ANIM"))
        {
            readANIMChunk(i, len);
        }
        else if (tag_str.equals("NODE"))
        {
            readNODEChunk(i, len);
        }
        else
        {
            System.out.println("    ?? (unknown chunk)");
            for (int n=0; n<len; n++) i.read();
        }
    }
    
    public static void main(String[] args) throws Exception
    {
        for (int n=0; n<args.length-1; n++)
        {
            if (args[n].equals("--no-vrts")) showVrts = false;
            if (args[n].equals("--no-keys")) showKeyframes = false;
        }
            
        FileInputStream i = new FileInputStream( new File(args[args.length - 1]) );
        
        readChunk(i, 0);
    }
}
