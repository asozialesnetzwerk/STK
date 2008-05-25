unit save_prj;

{$mode objfpc}{$H+}

interface

uses
  Classes, SysUtils,agfx_leveldesign_class,agfx_types;


  procedure SaveData();
  procedure LoadProject(filename:String);
  procedure ExportLevel(name:String);
  

implementation

uses main;


// *****************************************************************************
// SAVE PROJECT
// *****************************************************************************
procedure SaveData();
var
   data:TStringList;
   mx,my,sx,sy:integer;
   projectname:String;
begin
      data:=TStringList.Create();
      data.Clear();
      
      // get project name (from NEW level form)
      
      projectname:=frm_main.LEVEL.project_name;

      // write def file
      data.Add(frm_main.LEVEL.def_file_name);
      // write size x
      data.Add(INtToStr(frm_main.LEVEL.size.x));
      // write size y
      data.Add(INtToStr(frm_main.LEVEL.size.y));
      // write drv count
      data.Add(INtToStr(frm_main.LEVEL.drv_id_count));
      
      for mx:=0 to frm_main.LEVEL.size.x-1 do
          for my:=0 to frm_main.LEVEL.size.y-1 do
          begin
              data.Add(INtToStr(frm_main.LEVEL.cell[mx,my].item_road_id));
              data.Add(INtToStr(frm_main.LEVEL.cell[mx,my].item_obst_id));
              data.Add(INtToStr(frm_main.LEVEL.cell[mx,my].item_dec64_id));
              data.Add(INtToStr(frm_main.LEVEL.cell[mx,my].drv_id));
              data.Add(INtToStr(frm_main.LEVEL.cell[mx,my].drv_id_top));
              for sx:=0 to MAX_SUB_SIZE-1 do
              for sy:=0 to MAX_SUB_SIZE-1 do
              begin
                   data.Add(INtToStr(frm_main.LEVEL.cell[mx,my].item_decor_array[sx,sy].ID));
              end;
          end;
          
     data.SaveToFile(projectname);
  end;
  
// *****************************************************************************
// LOAD PROJECT
// *****************************************************************************
procedure LoadProject(filename:String);
var data:TStringList;
    i:integer;
    mx,my,sx,sy:integer;
    
    function getNextLine():String;
    var res:String;
    begin
       res:=data.Strings[i];
       Inc(i);
       result:=res;

    end;
    
    
begin
    data:=TStringList.Create;
    data.LoadFromFile(filename);

    frm_main.LEVEL.Free;
    
    frm_main.LEVEL:=TLevelGrid.Create();

    frm_main.LEVEL.ClearGrid();
      
    frm_main.LEVEL.project_name:=filename;

    i:=0;
    frm_main.LEVEL.def_file_name:=getNextLine();
    frm_main.LEVEL.size.x := StrToInt(getNextLine());
    frm_main.LEVEL.size.y := StrToInt(getNextLine());
    frm_main.LEVEL.drv_id_count:= StrToInt(getNextLine());

    for mx:=0 to frm_main.LEVEL.size.x-1 do
    begin
         for my:=0 to frm_main.LEVEL.size.y-1 do
         begin

              frm_main.LEVEL.cell[mx,my].item_road_id:=StrToInt(getNextLine());
              frm_main.LEVEL.cell[mx,my].item_obst_id:=StrToInt(getNextLine());
              frm_main.LEVEL.cell[mx,my].item_dec64_id:=StrToInt(getNextLine());
              frm_main.LEVEL.cell[mx,my].drv_id:=StrToInt(getNextLine());
              frm_main.LEVEL.cell[mx,my].drv_id_top:=StrToInt(getNextLine());
              for sx:=0 to MAX_SUB_SIZE-1 do
                  for sy:=0 to MAX_SUB_SIZE-1 do
                  begin
                       frm_main.LEVEL.cell[mx,my].item_decor_array[sx,sy].ID:=StrToInt(getNextLine());
                  end;
         end;
    end;

  frm_main.LEVEL.LevelItemDefinition.LoadFromFile(frm_main.EXE+'editor/definitions/'+frm_main.LEVEL.def_file_name);
  
  frm_main.LEVEL.Flags.bDefinition:=true;

  frm_main.LEVEL.view_pos.X:=0;
  frm_main.LEVEL.view_pos.Y:=0;
  frm_main.LEVEL.real_pos.x:=0;
  frm_main.LEVEL.real_pos.y:=0;
  frm_main.Caption:='STKed 2008 - ['+frm_main.LEVEL.project_name+']';

  frm_main.IconScrollBar.Position:=0;
  frm_main.IconScrollBar.Min:=0;
  frm_main.IconScrollBar.Max:=frm_main.LEVEL.LevelItemDefinition.count-12;

  frm_main.UpdateIconsByScrollBar();
  
  frm_main.LevelItemListBox.Clear();
  for i:=0 to frm_main.LEVEL.LevelItemDefinition.count-1 do
  begin
       frm_main.LevelItemListBox.Items.Add(frm_main.LEVEL.LevelItemDefinition.item[i].name);
  end;

  frm_main.MenuItem5.Enabled:=true;
  frm_main.MenuItem6.Enabled:=true;
  frm_main.MenuItem7.Enabled:=true;
  frm_main.LevelItemListBox.Selected[0]:=true;

  data.Free();
  
  frm_main.DrawMapGridFull();
end;

// *****************************************************************************
// EXPORT LEVEL
// *****************************************************************************
  
procedure ExportLevel(name:String);
var out_level:TStringList;
    mxx,myy,sx,sy:integer;
    ID:Integer;
    model:string;
    POS:TF3D_Vector3f;
    ROT:TF3D_Vector3f;
    
    
    procedure AddToFile(m:String;mx:integer;my:integer;p:TF3D_Vector3f;R:TF3D_Vector3f;typ:string;sx,sy:Integer;ev:String);
    var fx,fy,fz,fax,fay,faz:single;
    begin
         if (TYP='ROAD')then
         begin
              fx:=(mx*frm_main.LEVEL.Config.UNIT_SIZE)+p.x-(frm_main.LEVEL.Config.UNIT_SIZE/2);
              fy:=(my*frm_main.LEVEL.Config.UNIT_SIZE)+p.y-(frm_main.LEVEL.Config.UNIT_SIZE/2);
              fz:=0+p.z;
              
              fax:=r.x;
              fay:=r.y;
              faz:=r.z;
              
              out_level.add('"'+m+'",'+FLoatToStr(frm_main.LEVEL.Config.FLIP_X*fx)+','+FLoatToStr(frm_main.LEVEL.Config.FLIP_Y*fy)+','+FLoatToStr(fz)+','+FLoatToStr(frm_main.LEVEL.Config.MODEL_ANGLE+fax)+','+FLoatToStr(fay)+','+FLoatToStr(faz));
         end;
         
         if ((TYP='OBSTACLE') or (TYP='DECOR64')) then
         begin
              fx:=(mx*frm_main.LEVEL.Config.UNIT_SIZE)+p.x-(frm_main.LEVEL.Config.UNIT_SIZE/2);
              fy:=(my*frm_main.LEVEL.Config.UNIT_SIZE)+p.y-(frm_main.LEVEL.Config.UNIT_SIZE/2);
              fz:=0+p.z;

              fax:=r.x;
              fay:=r.y;
              faz:=r.z;

              if (UpperCase(ev)='NONE') then out_level.add('"'+m+'",'+FLoatToStr(frm_main.LEVEL.Config.FLIP_X*fx)+','+FLoatToStr(frm_main.LEVEL.Config.FLIP_Y*fy)+','+FLoatToStr(fz)+','+FLoatToStr(frm_main.LEVEL.Config.MODEL_ANGLE+fax)+','+FLoatToStr(fay)+','+FLoatToStr(faz));
              if (UpperCase(ev)='START') then out_level.add('"'+m+'",'+FLoatToStr(frm_main.LEVEL.Config.FLIP_X*fx)+','+FLoatToStr(frm_main.LEVEL.Config.FLIP_Y*fy)+','+FLoatToStr(fz)+','+FLoatToStr(frm_main.LEVEL.Config.MODEL_ANGLE+fax)+','+FLoatToStr(fay)+','+FLoatToStr(faz));
              if (UpperCase(ev)='AUTOZ') then out_level.add('"'+m+'",'+FLoatToStr(frm_main.LEVEL.Config.FLIP_X*fx)+','+FLoatToStr(frm_main.LEVEL.Config.FLIP_Y*fy)+',{},'+FLoatToStr(frm_main.LEVEL.Config.MODEL_ANGLE+fax)+','+FLoatToStr(fay)+','+FLoatToStr(faz));
         end;

         

         if (TYP='DECOR16') then
         begin
              fx:=((mx*frm_main.LEVEL.Config.UNIT_SIZE)+(sx*frm_main.LEVEL.Config.UNIT_SIZE/4))+p.x-(frm_main.LEVEL.Config.UNIT_SIZE/2)-(frm_main.LEVEL.Config.UNIT_SIZE/8);
              fy:=((my*frm_main.LEVEL.Config.UNIT_SIZE)+(sy*frm_main.LEVEL.Config.UNIT_SIZE/4))+p.y-(frm_main.LEVEL.Config.UNIT_SIZE/2)-(frm_main.LEVEL.Config.UNIT_SIZE/8);
              fz:=p.z;

              fax:=r.x;
              fay:=r.y;
              faz:=r.z;

              if (UpperCase(ev)='NONE') then out_level.add('"'+m+'",'+FLoatToStr(frm_main.LEVEL.Config.FLIP_X*fx)+','+FLoatToStr(frm_main.LEVEL.Config.FLIP_Y*fy)+','+FLoatToStr(fz)+','+FLoatToStr(frm_main.LEVEL.Config.MODEL_ANGLE+fax)+','+FLoatToStr(fay)+','+FLoatToStr(faz));
              if (UpperCase(ev)='AUTOZ') then out_level.add('"'+m+'",'+FLoatToStr(frm_main.LEVEL.Config.FLIP_X*fx)+','+FLoatToStr(frm_main.LEVEL.Config.FLIP_Y*fy)+',{},'+FLoatToStr(frm_main.LEVEL.Config.MODEL_ANGLE+fax)+','+FLoatToStr(fay)+','+FLoatToStr(faz));
              if (UpperCase(ev)='HERRING') then out_level.add(ev+','+FLoatToStr(frm_main.LEVEL.Config.FLIP_X*fx)+','+FLoatToStr(frm_main.LEVEL.Config.FLIP_Y*fy))


         end;
    end;

begin

     out_level:=TStringList.Create();
     
     
     // LOC FILE
     out_level.Add('# Created by STUXE 2008 Editor.');
     out_level.Add('#');

     for mxx:=0 to frm_main.LEVEL.size.x-1 do
          for myy:=0 to frm_main.LEVEL.size.y-1 do
          begin

              ID:=frm_main.LEVEL.cell[mxx,myy].item_road_id;

              model:=frm_main.LEVEL.LevelItemDefinition.item[ID].model_file;
              POS:=frm_main.LEVEL.LevelItemDefinition.item[ID].position;
              ROT:=frm_main.LEVEL.LevelItemDefinition.item[ID].rotation;
              
              AddToFile(model,mxx,myy,POS,ROT,'ROAD',0,0,'none');
              

              ID:=frm_main.LEVEL.cell[mxx,myy].item_obst_id;


              if ID>=0 then
              begin
                   model:=frm_main.LEVEL.LevelItemDefinition.item[ID].model_file;
                   POS:=frm_main.LEVEL.LevelItemDefinition.item[ID].position;
                   ROT:=frm_main.LEVEL.LevelItemDefinition.item[ID].rotation;

                   AddToFile(model,mxx,myy,POS,ROT,'OBSTACLE',0,0,'none');
              end;

              for sx:=0 to MAX_SUB_SIZE-1 do
              for sy:=0 to MAX_SUB_SIZE-1 do
              begin

                   ID:=frm_main.LEVEL.cell[mxx,myy].item_decor_array[sx,sy].ID;
                   if ID>=0 then
                   begin
                        model:=frm_main.LEVEL.LevelItemDefinition.item[ID].model_file;
                        POS:=frm_main.LEVEL.LevelItemDefinition.item[ID].position;
                        ROT:=frm_main.LEVEL.LevelItemDefinition.item[ID].rotation;

                        AddToFile(model,mxx,myy,POS,ROT,'DECOR16',sx-1,sy-1,frm_main.LEVEL.LevelItemDefinition.item[ID].event);
                   end;
              end;
          end;


     if frm_main.LEVEL.COnfig.bLOC then out_level.SaveToFile(frm_main.LEVEL.COnfig.export_path+'/'+name+'.loc');
     
     // DRVL FILE
     out_level.Clear();
     if frm_main.LEVEL.COnfig.bDRVL then frm_main.LEVEL.DrvL_List.SaveToFile(frm_main.LEVEL.COnfig.export_path+'/'+name+'.drvl');

     // DRVR FILE
     out_level.Clear();
     if frm_main.LEVEL.COnfig.bDRVR then frm_main.LEVEL.DrvR_List.SaveToFile(frm_main.LEVEL.COnfig.export_path+'/'+name+'.drvr');
     
     // TRACK FILE
     out_level.Clear();
     
     out_level.Add(';; -*- mode: lisp -*-');
     out_level.Add('');
     out_level.Add('(tuxkart-track');
     out_level.Add(' (name                   "'+name+'")');
     out_level.Add(' (description            "Created by Andy&Baskervil")');
     out_level.Add(' (music                  "'+frm_main.LEVEL.Config.ogg+'")');
     out_level.Add(' (screenshot             "'+frm_main.LEVEL.Config.sshot+'")');
     out_level.Add(' (topview                "'+frm_main.LEVEL.Config.topview+'")');
     
     out_level.Add(' (start-x 5)');
     out_level.Add(' (start-y -15)');
     
     out_level.Add(' (AI-curve-speed-adjust  2.0)');
     out_level.Add(' (AI-angle-adjust        2.7)');
     out_level.Add(')');
     out_level.Add(';; EOF ;;');

     if frm_main.LEVEL.COnfig.bTRACK then out_level.SaveToFile(frm_main.LEVEL.COnfig.export_path+'/'+name+'.track');


     out_level.Clear();


out_level.Add(';; -*- mode: lisp -*-');
out_level.Add('');
out_level.Add('(herring');
out_level.Add('  (gold   "'+frm_main.LEVEL.Config.yherring+'"  )');
out_level.Add('  (silver "'+frm_main.LEVEL.Config.sherring+'")');
out_level.Add('  (green  "'+frm_main.LEVEL.Config.gherring+'"    )');
out_level.Add('  (red    "'+frm_main.LEVEL.Config.rherring+'")');
out_level.Add(')');
out_level.Add('');
out_level.Add(';; EOF ;;');

   if frm_main.LEVEL.COnfig.bHERRING then out_level.SaveToFile(frm_main.LEVEL.COnfig.export_path+'/'+name+'.herring');
     out_level.free();

end;
  
  
end.

