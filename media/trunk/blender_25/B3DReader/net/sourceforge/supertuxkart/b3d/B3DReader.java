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

    
    public static int readInt(InputStream i) throws Exception
    {
        byte[] b_len = new byte[4];
        if (i.read(b_len) != 4)
        {
            throw new RuntimeException("Can't read int");
        }
        
        int len = ((b_len[0] & 0xFF) | ((b_len[1] & 0xFF) << 8) | ((b_len[2] & 0xFF) << 16) | ((b_len[3] & 0xFF) << 24));
        return len;
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
        int packed_bytes = readInt(i);
        return Float.intBitsToFloat(packed_bytes);
    }
    
    public static void readBB3DChunk(InputStream i, final int length) throws Exception
    {
        int version = readInt(i);
        System.out.println("    Version: " + version);
        
        while (i.available() > 0) {
            readChunk(i, 1);
        }
    }
    
    public static void readTEXSChunk(InputStream i, final int length) throws Exception
    {
        int read = 0;
        
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
            
            System.out.println("        Filename: " + filename);
            System.out.println("        Flags: " + flags);
            System.out.println("        Blend: " + blend);
            System.out.println("        Position: (" + x + ", " + y + ")");
            System.out.println("        Scale: (" + x_scale + ", " + y_scale + ")");
            System.out.println("        Rotation: " + rot);
        }
    }
    
    public static void readBRUSChunk(InputStream i, final int length) throws Exception
    {
        int num = readInt(i);
        int read = 4;
        
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

            System.out.println("        Material name: " + name);
            System.out.println("        RGBA: (" + r + ", " + g + ", " + b + ", " + a + ")");
            System.out.println("        Shininess: " + shininess);
            System.out.println("        Blend: " + blend);
            System.out.println("        FX: " + fx);
            
            
            for (int n=0; n<num; n++)
            {
                int tid = readInt(i);
                read += 4;
                System.out.println("        TextureID[" + n + "] : " + tid);
            }
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
            
            System.out.println("            Vertex: (" + x + ", " + y + ", " + z + ")");
            
            if ((flags & 0x1) != 0)
            {
                float nx = readFloat(i);
                float ny = readFloat(i);
                float nz = readFloat(i);
                read += 12;
                
                System.out.println("            Normal: (" + nx + ", " + ny + ", " + nz + ")");
            }
            
            if ((flags & 0x2) != 0)
            {
                float r = readFloat(i);
                float g = readFloat(i);
                float b = readFloat(i);
                float a = readFloat(i);
                read += 16;
                
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
                System.out.println("            TexCoord: ( " + coords + ")");
            }
        }
    }
    
    public static void readTRISChunk(InputStream i, final int length) throws Exception
    {
        int brush_id = readInt(i);
        System.out.println("        BrushID: " + brush_id);
        
        int read = 4;
        
        while (read < length)
        {
            int vertex_1 = readInt(i);
            int vertex_2 = readInt(i);
            int vertex_3 = readInt(i);
            read += 12;
            System.out.println("        Triangle: (" + vertex_1 + ", " + vertex_2 + ", " + vertex_3 + ")");
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
            System.out.println("        Frame: " + frame);
            
            if ((flags & 0x1) != 0)
            {
                float x = readFloat(i);
                float y = readFloat(i);
                float z = readFloat(i);
                read += 12;
                System.out.println("            Position: (" + x + ", " + y + ", " + z + ")");
            }
            if ((flags & 0x2) != 0)
            {
                float x = readFloat(i);
                float y = readFloat(i);
                float z = readFloat(i);
                read += 12;
                System.out.println("            Scale: (" + x + ", " + y + ", " + z + ")");
            }
            if ((flags & 0x4) != 0)
            {
                float w = readFloat(i);
                float x = readFloat(i);
                float y = readFloat(i);
                float z = readFloat(i);
                read += 16;
                System.out.println("            Rot: (" + w  + ", " + x + ", " + y + ", " + z + ")");
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
        System.out.println("        Position: (" + x + ", " + y + ", " + z + ")");
        System.out.println("        Scale: (" + x_scale + ", " + y_scale + ", " + z_scale + ")");
        System.out.println("        Rotation: (" + w_rot + ", " + x_rot + ", " + y_rot + ", " + z_rot + ")");
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
        System.out.println(tag_str + " (" + len + " bytes)");
        
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
        FileInputStream i = new FileInputStream( new File(args[0]) );
        
        readChunk(i, 0);
    }
}
