unit agfx_leveldesign_class;
// *****************************************************************************
//
// *****************************************************************************
{$mode objfpc}{$H+}

interface

uses
  Classes, SysUtils,agfx_types,agfx_definition_class,agfx_config,frm_drv_cont_unit,agfx_helpers;

const
// *****************************************************************************
//
// *****************************************************************************
MAX_LEVEL_WIDTH=100;
MAX_LEVEL_HEIGHT=100;
MAX_SUB_SIZE = 4;
// *****************************************************************************
//
// *****************************************************************************
type TDrvData=record
     cx,cy:integer;
     id:integer;
     end;


// *****************************************************************************
//
// *****************************************************************************
type TSubCelItem=record
     ID:Integer;
     end;
// *****************************************************************************
//
// *****************************************************************************
type TLevelCell=record
     drv_id:integer;
     drv_id_top:integer;
     item_road_id:integer;
     item_obst_id:integer;
     item_dec64_id:integer;

     
     item_decor_array:array[0..MAX_SUB_SIZE-1,0..MAX_SUB_SIZE-1] of TSubCelItem
     end;

type TLevelFlags =record
     bDefinition:boolean;
     bGrid:boolean;
     end;
// *****************************************************************************
//
// *****************************************************************************
type TLevelGrid = class
     size:TF3D_Vector2i;
     view_pos:TF3D_Vector2i;
     mouse_pos:TF3D_Vector2i;
     mouse_SUB_pos:TF3D_Vector2i;
     real_pos:TF3D_Vector2i;
     Flags:TLevelFlags;
     project_name:String;
     def_file_name:String;
     config:TConfig;
     dst_drv_layer:integer;
     DrvR_List:TStringList;
     DrvL_List:TStringList;
     drv_id_count:integer;

     cell:array[0..MAX_LEVEL_WIDTH-1,0 .. MAX_LEVEL_HEIGHT-1] of  TLevelCell;
     private

     public
         LevelItemDefinition:TLevelItemList;
         constructor Create;
         destructor Destroy;
         procedure ClearGrid();
         procedure SetCell(_x,_y:integer;name:string;id:integer);
         procedure SetCellDRV(_x,_y:integer);
         function GetCell(_x,_y:integer;src_cell:String):integer;
         function GetCellDRV(_x,_y:integer;pos:string):integer;
         procedure SetSubCell(_x,_y,_sx,_sy:integer;name:string;id:integer);
         function GetSubCell(_x,_y,_sx,_sy:integer;src_cell:String):integer;
         function GetAllCell():TLevelCell;
         procedure SetAllCell(c:TLevelCell);
         procedure PrepareDriveLine(dbg:boolean);
         function Get_item_by_DrvID(id:integer):TDrvData;
     end;

implementation
uses main;
// *****************************************************************************
//
// *****************************************************************************
constructor TLevelGrid.Create;
begin
     Inherited create;
     self.LevelItemDefinition:=TLevelItemList.Create();
     self.config := TConfig.Create();
     self.config.LoadFromFile('editor/editor.cfg');
     self.Flags.bDefinition:=false;
     self.Flags.bGrid:=false;
     DrvR_List:=TStringList.Create();
     DrvL_List:=TStringList.Create();
end;

// *****************************************************************************
//
// *****************************************************************************
destructor TLevelGrid.Destroy;
begin
     self.LevelItemDefinition.free();
     self.config.free();
     inherited destroy;
end;

// *****************************************************************************
//
// *****************************************************************************
procedure TLevelGrid.ClearGrid();
var x:integer;
    y:integer;
    dx,dy:integer;
begin

     self.drv_id_count:=0;
     for x:=0 to MAX_LEVEL_WIDTH-1 do
         for y:=0 to MAX_LEVEL_HEIGHT-1 do
         begin
              self.cell[x,y].item_road_id:=0;
              self.cell[x,y].item_obst_id:=-1;
              self.cell[x,y].item_dec64_id:=-1;
              self.cell[x,y].drv_id:=-1;
              self.cell[x,y].drv_id_top:=-1;

              for dx:=0 to MAX_SUB_SIZE-1 do
              for dy:=0 to MAX_SUB_SIZE-1 do
                  begin
                       self.cell[x,y].item_decor_array[dx,dy].ID:=-1;
                  end;

         end;

         
end;

procedure TLevelGrid.SetCell(_x,_y:integer;name:string;id:integer);
var dx,dy:integer;
begin

     if (self.LevelItemDefinition.item[id].ItemType='ROAD')then
     begin
        self.cell[_x+self.view_pos.x,_y+self.view_pos.y].item_road_id:=id;
     end;
     
     if (self.LevelItemDefinition.item[id].ItemType='GROUND')then
     begin
        self.cell[_x+self.view_pos.x,_y+self.view_pos.y].item_road_id:=id;
     end;
     
     if (self.LevelItemDefinition.item[id].ItemType='OBSTACLE') then
     begin
        self.cell[_x+self.view_pos.x,_y+self.view_pos.y].item_obst_id:=id;
     end;

     if (self.LevelItemDefinition.item[id].ItemType='BRIDGE') then
     begin
        self.cell[_x+self.view_pos.x,_y+self.view_pos.y].item_obst_id:=id;
     end;
     
     if (self.LevelItemDefinition.item[id].ItemType='DECOR64') then
     begin
        self.cell[_x+self.view_pos.x,_y+self.view_pos.y].item_dec64_id:=id;
     end;
     
     if (self.LevelItemDefinition.item[id].ItemType='CLEAR')then
     begin
        self.cell[_x+self.view_pos.x,_y+self.view_pos.y].item_road_id:=id;
        self.cell[_x+self.view_pos.x,_y+self.view_pos.y].item_obst_id:=-1;

        for dx:=0 to MAX_SUB_SIZE-1 do
        for dy:=0 to MAX_SUB_SIZE-1 do self.cell[_x+self.view_pos.x,_y+self.view_pos.y].item_decor_array[dx,dy].ID:=-1;
     end;
     
end;

procedure TLevelGrid.SetCellDRV(_x,_y:integer);
var dx,dy:integer;
    l0_type,l1_type:string;
    L0_id,L1_id:Integer;
begin


     l0_type:='';
     l1_type:='';
     // is OBSTACLE
     L1_ID:= self.cell[_x+self.view_pos.x,_y+self.view_pos.y].item_obst_id;
     // is ROAD
     L0_ID:= self.cell[_x+self.view_pos.x,_y+self.view_pos.y].item_road_id;

     // when is engaged -> EXIT
     if ((self.cell[_x+self.view_pos.x,_y+self.view_pos.y].drv_id_top<>-1) and
         (self.cell[_x+self.view_pos.x,_y+self.view_pos.y].drv_id<>-1)) then exit;


     // ROAD = exist / BRIDGE = missing
     if ((L0_ID<>-1) and (L1_ID=-1) and
         (self.cell[_x+self.view_pos.x,_y+self.view_pos.y].drv_id_top=-1) and
         (self.cell[_x+self.view_pos.x,_y+self.view_pos.y].drv_id=-1)) then
     begin
          L0_type:=self.LevelItemDefinition.item[L0_ID].ItemType;
          if (L0_type='ROAD')  then
          begin
              self.cell[_x+self.view_pos.x,_y+self.view_pos.y].drv_id:=self.drv_id_count;
              inc(self.drv_id_count);
          end;
     end;
     
     
     // ROAD = missing / BRIDGE = exist
     if ((L1_ID<>-1) and (L0_ID=0)  and
         (self.cell[_x+self.view_pos.x,_y+self.view_pos.y].drv_id_top=-1) and
         (self.cell[_x+self.view_pos.x,_y+self.view_pos.y].drv_id=-1)) then
     begin
          L1_type:=self.LevelItemDefinition.item[L1_ID].ItemType;
          if (L1_type='BRIDGE')  then
          begin
              self.cell[_x+self.view_pos.x,_y+self.view_pos.y].drv_id_top:=self.drv_id_count;
              inc(self.drv_id_count);
          end;
     end;

     if ((L1_ID<>-1) and (L0_ID<>-1))  then
     begin
     
         L0_type:=self.LevelItemDefinition.item[L0_ID].ItemType;
         L1_type:=self.LevelItemDefinition.item[L1_ID].ItemType;
         if ((L0_type='ROAD') and (L1_type='BRIDGE')) then
         begin
              frm_drv_cont.ShowModal;
         
              // continue on ROAD
              if self.dst_drv_layer=0 then
              begin
                   self.cell[_x+self.view_pos.x,_y+self.view_pos.y].drv_id:=self.drv_id_count;
                   inc(self.drv_id_count);
                   frm_main.DrawMapGridFull();
              end;

              // continue on BRIDGE
              if self.dst_drv_layer=1 then
              begin
                   self.cell[_x+self.view_pos.x,_y+self.view_pos.y].drv_id_top:=self.drv_id_count;
                   inc(self.drv_id_count);
                   frm_main.DrawMapGridFull();
              end;
         end;
     end;

end;

function TLevelGrid.GetAllCell():TLevelCell;
var res:integer;
begin
     result:=self.cell[self.mouse_pos.x+self.view_pos.x,self.mouse_pos.y+self.view_pos.y];

end;

procedure TLevelGrid.SetAllCell(c:TLevelCell);
var res:integer;
begin
     self.cell[self.mouse_pos.x+self.view_pos.x,self.mouse_pos.y+self.view_pos.y]:=c;

end;

function TLevelGrid.GetCell(_x,_y:integer;src_cell:String):integer;
var res:integer;
begin
     if ((src_cell='ROAD') or (src_cell='GROUND'))then
        res:=self.cell[_x+self.view_pos.x,_y+self.view_pos.y].item_road_id;
     if ((src_cell='OBSTACLE') or (src_cell='BRIDGE'))then
        res:=self.cell[_x+self.view_pos.x,_y+self.view_pos.y].item_obst_id;
     if (src_cell='DECOR64')then
        res:=self.cell[_x+self.view_pos.x,_y+self.view_pos.y].item_dec64_id;

     result:=res;

end;

function TLevelGrid.GetCellDRV(_x,_y:integer;pos:string):integer;
var res:integer;
begin
        if (pos='BOTTOM') then res:=self.cell[_x+self.view_pos.x,_y+self.view_pos.y].drv_id;
        if (pos='TOP') then res:=self.cell[_x+self.view_pos.x,_y+self.view_pos.y].drv_id_top;
        
        result:=res;
end;


procedure TLevelGrid.SetSubCell(_x,_y,_sx,_sy:integer;name:string;id:integer);
var dx,mx,my,dy:double;
begin

     if (self.LevelItemDefinition.item[id].ItemType='DECOR16')then
     begin
        self.cell[_x+self.view_pos.x,_y+self.view_pos.y].item_decor_array[_sx,_sy].ID:=id;

     end;

end;


function TLevelGrid.GetSubCell(_x,_y,_sx,_sy:integer;src_cell:String):integer;
var res:integer;
begin
     if (src_cell='DECOR16')then
     begin
        res:=self.cell[_x+self.view_pos.x,_y+self.view_pos.y].item_decor_array[_sx,_sy].ID;
     end;
     
     result:=res;
end;

function TLevelGrid.Get_item_by_DrvID(id:integer):TDrvData;
var cx,cy:integer;
    res:TDrvData;
begin
     for cx:=0 to self.size.x-1 do
     for cy:=0 to self.size.x-1 do
     begin
           if self.cell[cx,cy].drv_id = id then
           begin
                res.cx := cx;
                res.cy := cy;
                res.id:= self.cell[cx,cy].item_road_id;
           end;
           if self.cell[cx,cy].drv_id_top = id then
           begin
                res.cx := cx;
                res.cy := cy;
                res.id := self.cell[cx,cy].item_obst_id;
           end;

     end;
     
     result := res;
end;


procedure TLevelGrid.PrepareDriveLine(dbg:boolean);
var item_id,i:Integer;
    ItemD:TDrvData;
    sx,sy,sz:single;
    
    i_LA:TF3D_Vector3f;
    i_RA:TF3D_Vector3f;
    i_ang:single;

    i_rot_LA:TF3D_Vector3f;
    i_rot_RA:TF3D_Vector3f;
    final_POINT:TF3D_Vector3f;
    id_name:String;
    
begin

     // clean
     self.DrvL_List.Clear;
     self.DrvR_List.Clear;
     
     for i:=0 to self.drv_id_count-1 do
     begin
        itemD:=self.Get_item_by_DrvID(i);

        sx:=(itemD.cx*frm_main.LEVEL.Config.UNIT_SIZE)-(frm_main.LEVEL.Config.UNIT_SIZE/2);
        sy:=(itemD.cy*frm_main.LEVEL.Config.UNIT_SIZE)-(frm_main.LEVEL.Config.UNIT_SIZE/2);
        sz:=0;

        i_ang:=self.LevelItemDefinition.item[itemD.id].rotation.X;
        
        i_LA:=self.LevelItemDefinition.item[itemD.id].drvl_A;
        i_rot_LA:=GetRotatedDRV(i_LA,i_ang);
        id_name:=self.LevelItemDefinition.item[itemD.id].name;
        final_POINT.x:= sx + i_rot_LA.x;
        final_POINT.y:= -sy + i_rot_LA.y;
        final_POINT.z:= sz + i_rot_LA.z;

        if dbg then
        begin
             final_POINT.x:=i_rot_LA.x;
             final_POINT.y:=i_rot_LA.y;
             final_POINT.z:=i_rot_LA.z;
        end;


        if dbg then
           self.DrvL_List.Add(format('%10s [%d,%d] = %f,%f,%f',[id_name,itemD.cx,itemD.cy,final_POINT.x,final_POINT.y,final_POINT.z]))
        else
            self.DrvL_List.Add(FloatToStr(final_POINT.x)+','+FloatToStr(final_POINT.y)+','+FloatToStr(final_POINT.z));

        
        i_RA:=self.LevelItemDefinition.item[itemD.id].drvr_A;
        i_rot_RA:=GetRotatedDRV(i_RA,i_ang);
        
        final_POINT.x:= sx + i_rot_RA.x;
        final_POINT.y:= -sy + i_rot_RA.y;
        final_POINT.z:= sz + i_rot_RA.z;

        if dbg then
        begin
             final_POINT.x:=i_rot_RA.x;
             final_POINT.y:=i_rot_RA.y;
             final_POINT.z:=i_rot_RA.z;
        end;

        if dbg then
            self.DrvR_List.Add(format('%10s [%d,%d] = %f,%f,%f',[id_name,itemD.cx,itemD.cy,final_POINT.x,final_POINT.y,final_POINT.z]))
        else
            self.DrvR_List.Add(FloatToStr(final_POINT.x)+','+FloatToStr(final_POINT.y)+','+FloatToStr(final_POINT.z));
        
        
     end;

end;


end.

