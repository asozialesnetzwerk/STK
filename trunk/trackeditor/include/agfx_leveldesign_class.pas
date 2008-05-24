unit agfx_leveldesign_class;
// *****************************************************************************
//
// *****************************************************************************
{$mode objfpc}{$H+}

interface

uses
  Classes, SysUtils,agfx_types,agfx_definition_class,agfx_config;

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
     end;

implementation

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


     if ((self.cell[_x+self.view_pos.x,_y+self.view_pos.y].drv_id_top<>-1) and
         (self.cell[_x+self.view_pos.x,_y+self.view_pos.y].drv_id<>-1)) then exit;
     
     if ((L1_ID<>-1) and
         (self.cell[_x+self.view_pos.x,_y+self.view_pos.y].drv_id_top=-1) and
         (self.cell[_x+self.view_pos.x,_y+self.view_pos.y].drv_id<>-1)) then
     begin
          L1_type:=self.LevelItemDefinition.item[L1_ID].ItemType;
          if (L1_type='BRIDGE') or ((L1_type='ROAD')) then
          begin
              self.cell[_x+self.view_pos.x,_y+self.view_pos.y].drv_id_top:=self.drv_id_count;
              inc(self.drv_id_count);
          end;
     end;

     if ((L0_ID<>-1) and
         (self.cell[_x+self.view_pos.x,_y+self.view_pos.y].drv_id_top=-1) and
         (self.cell[_x+self.view_pos.x,_y+self.view_pos.y].drv_id=-1)) then
     begin
          L0_type:=self.LevelItemDefinition.item[L0_ID].ItemType;
          if (L0_type='BRIDGE') or ((L0_type='ROAD')) then
          begin
              self.cell[_x+self.view_pos.x,_y+self.view_pos.y].drv_id:=self.drv_id_count;
              inc(self.drv_id_count);
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




end.

