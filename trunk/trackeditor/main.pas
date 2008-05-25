unit main;

{$mode objfpc}{$H+}

interface

uses
  Classes, SysUtils, LResources, Forms, Controls, Graphics,
  agfx_leveldesign_class,frm_new,save_prj,frm_eportdone_unit, frm_exp_track_unit,
  Dialogs, StdCtrls, ExtCtrls, Menus, DbCtrls;

type

  { Tfrm_main }

  Tfrm_main = class(TForm)
    chk_drv_num: TCheckBox;
    GroupBox1: TGroupBox;
    GroupBox2: TGroupBox;
    Image1: TImage;
    item_image_1: TImage;
    img_none: TImage;
    img_SelectedIcon: TImage;
    item_image_10: TImage;
    item_image_11: TImage;
    item_image_12: TImage;
    item_image_2: TImage;
    item_image_3: TImage;
    item_image_4: TImage;
    item_image_5: TImage;
    item_image_6: TImage;
    item_image_7: TImage;
    item_image_8: TImage;
    item_image_9: TImage;
    Label1: TLabel;
    lbl_sel_name: TLabel;
    lbl_type: TLabel;
    LevelItemListBox: TListBox;
    MainMenu1: TMainMenu;
    MenuItem1: TMenuItem;
    MenuItem10: TMenuItem;
    MenuItem11: TMenuItem;
    MenuItem12: TMenuItem;
    MenuItem13: TMenuItem;
    MenuItem14: TMenuItem;
    MenuItem15: TMenuItem;
    MenuItem16: TMenuItem;
    MenuItem17: TMenuItem;
    MenuItem18: TMenuItem;
    MenuItem2: TMenuItem;
    MenuItem3: TMenuItem;
    MenuItem4: TMenuItem;
    MenuItem5: TMenuItem;
    MenuItem6: TMenuItem;
    MenuItem7: TMenuItem;
    MenuItem8: TMenuItem;
    LevelPaintBox: TPaintBox;
    chk_road: TRadioButton;
    chk_obstacle: TRadioButton;
    chk_decor: TRadioButton;
    MenuItem9: TMenuItem;
    OpenDialogPrj: TOpenDialog;
    Panel1: TPanel;
    Panel2: TPanel;
    Panel3: TPanel;
    Panel4: TPanel;
    GridPopupMenu: TPopupMenu;
    chk_decor64: TRadioButton;
    SaveDialogPrj: TSaveDialog;
    IconScrollBar: TScrollBar;
    ScrollBar_x_cell: TScrollBar;
    ScrollBar_y_cell: TScrollBar;
    Timer1: TTimer;
    procedure chk_drv_numChange(Sender: TObject);
    procedure FormCreate(Sender: TObject);
    procedure FormPaint(Sender: TObject);
    procedure FormShow(Sender: TObject);
    procedure IconScrollBarChange(Sender: TObject);
    procedure item_image_1Click(Sender: TObject);
    procedure LevelItemListBoxClick(Sender: TObject);
    procedure LevelPaintBoxClick(Sender: TObject);
    procedure LevelPaintBoxMouseDown(Sender: TObject; Button: TMouseButton;
      Shift: TShiftState; X, Y: Integer);
    procedure LevelPaintBoxMouseMove(Sender: TObject; Shift: TShiftState; X,
      Y: Integer);
    procedure LevelPaintBoxMouseUp(Sender: TObject; Button: TMouseButton;
      Shift: TShiftState; X, Y: Integer);
    procedure MenuItem11Click(Sender: TObject);
    procedure MenuItem12Click(Sender: TObject);
    procedure MenuItem13Click(Sender: TObject);
    procedure MenuItem14Click(Sender: TObject);
    procedure MenuItem15Click(Sender: TObject);
    procedure MenuItem16Click(Sender: TObject);
    procedure MenuItem17Click(Sender: TObject);
    procedure MenuItem18Click(Sender: TObject);
    procedure MenuItem3Click(Sender: TObject);
    procedure MenuItem4Click(Sender: TObject);
    procedure MenuItem5Click(Sender: TObject);
    procedure MenuItem6Click(Sender: TObject);
    procedure MenuItem7Click(Sender: TObject);
    procedure MenuItem8Click(Sender: TObject);
    procedure MenuItem9Click(Sender: TObject);
    procedure ScrollBar_x_cellChange(Sender: TObject);
    procedure ScrollBar_x_cellScroll(Sender: TObject; ScrollCode: TScrollCode;var ScrollPos: Integer);
    procedure ScrollBar_y_cellChange(Sender: TObject);
    procedure ScrollBar_y_cellScroll(Sender: TObject; ScrollCode: TScrollCode;var ScrollPos: Integer);
    procedure Timer1Timer(Sender: TObject);
    procedure UpdateIconsByScrollBar();

  private
    { private declarations }
  public
    { public declarations }
    SelectedItemID:Integer;
    LEVEL:TLevelGrid;
    lm_button:integer;
    rm_button:integer;
    cursor_mode:integer;
    counter:integer;
    EXE:String;
    
    TMP_CELL:TLevelCell;
    bTMP_CELL:boolean;
    procedure DrawMapGrid();
    procedure DrawMapGridFull();
    procedure DrawMapCursor();
    procedure UpdateLevel();
    
  end; 

var
  frm_main: Tfrm_main;

implementation

{ Tfrm_main }

// *****************************************************************************
// MAIN:
// *****************************************************************************
procedure Tfrm_main.FormCreate(Sender: TObject);
begin

  DECIMALSEPARATOR:='.';
  LEVEL:=TLevelGrid.Create();
  cursor_mode:=0;
  EXE:=ExtractFilePath(Application.ExeName);
  counter:=0;
  self.Timer1.interval := self.LEVEL.config.refresh;
  bTMP_CELL:=false;
end;

procedure Tfrm_main.chk_drv_numChange(Sender: TObject);
begin
  DrawMapGridFull();
end;

// *****************************************************************************
// MAIN:
// *****************************************************************************
procedure Tfrm_main.FormPaint(Sender: TObject);
var i:integer;
   x:integer;
    y:integer;
begin

    self.UpdateLevel();

     
end;

procedure Tfrm_main.FormShow(Sender: TObject);
begin
  self.MenuItem5.Enabled:=false;
  self.MenuItem6.Enabled:=false;
  self.MenuItem7.Enabled:=false;
end;

procedure Tfrm_main.IconScrollBarChange(Sender: TObject);
begin
  if LEVEL.Flags.bDefinition=false then exit;
  self.UpdateIconsByScrollBar();
end;

procedure Tfrm_main.item_image_1Click(Sender: TObject);
var item_id:integer;
    img_file,img_map:String;
begin
  if LEVEL.Flags.bDefinition=false then exit;

     item_id := (Sender as TImage).Tag + self.IconScrollBar.Position;
     SelectedItemID:=item_id;

     lbl_sel_name.Caption:=LEVEL.LevelItemDefinition.item[item_id].name;
     lbl_type.Caption:='Type: '+LEVEL.LevelItemDefinition.item[item_id].itemtype;
     img_file:='editor/icons/'+LEVEL.LevelItemDefinition.item[item_id].image_iso_file;
     img_map:='editor/icons/'+LEVEL.LevelItemDefinition.item[item_id].image_file;

     if not(FileExists(img_file)) then
     begin
          img_file:='editor/icons/icon_none.png';
          lbl_type.Caption:='Type:<none>';
          lbl_sel_name.Caption:='<noname>';
     end;

     if not(FileExists(img_map)) then
     begin
          img_map:='editor/icons/none1.png';
          lbl_type.Caption:='Type:<none>';
          lbl_sel_name.Caption:='<noname>';
     end;

     img_SelectedIcon.Picture.LoadFromFile(img_file);

     cursor_mode:=0;

     if ((LEVEL.LevelItemDefinition.item[item_id].itemtype='ROAD') or
         (LEVEL.LevelItemDefinition.item[item_id].itemtype='GROUND') or
         (LEVEL.LevelItemDefinition.item[item_id].itemtype='CLEAN')) then self.chk_road.Checked:=true;

     if ((LEVEL.LevelItemDefinition.item[item_id].itemtype='OBSTACLE') or
         (LEVEL.LevelItemDefinition.item[item_id].itemtype='BRIDGE')) then self.chk_obstacle.Checked:=true;

     if (LEVEL.LevelItemDefinition.item[item_id].itemtype='DECOR64')then self.chk_decor64.Checked:=true;


     if (LEVEL.LevelItemDefinition.item[item_id].itemtype='DECOR16')then
     begin
          self.chk_decor.Checked:=true;
          cursor_mode:=1;
     end;

end;

// *****************************************************************************
// MAIN:
// *****************************************************************************
procedure Tfrm_main.LevelItemListBoxClick(Sender: TObject);
var img_file:String;
    img_map:String;
begin
      if LEVEL.Flags.bDefinition=false then exit;
      
     lbl_sel_name.Caption:=LEVEL.LevelItemDefinition.item[LevelItemListBox.ItemIndex].name;
     lbl_type.Caption:='Type: '+LEVEL.LevelItemDefinition.item[LevelItemListBox.ItemIndex].itemtype;
     img_file:='editor/icons/'+LEVEL.LevelItemDefinition.item[LevelItemListBox.ItemIndex].image_iso_file;
     img_map:='editor/icons/'+LEVEL.LevelItemDefinition.item[LevelItemListBox.ItemIndex].image_file;
     
     if not(FileExists(img_file)) then
     begin
          img_file:='editor/icons/icon_none.png';
          lbl_type.Caption:='Type:<none>';
          lbl_sel_name.Caption:='<noname>';
     end;

     if not(FileExists(img_map)) then
     begin
          img_map:='editor/icons/none1.png';
          lbl_type.Caption:='Type:<none>';
          lbl_sel_name.Caption:='<noname>';
     end;
     
     img_SelectedIcon.Picture.LoadFromFile(img_file);

     cursor_mode:=0;
     
     if ((LEVEL.LevelItemDefinition.item[LevelItemListBox.ItemIndex].itemtype='ROAD') or
         (LEVEL.LevelItemDefinition.item[LevelItemListBox.ItemIndex].itemtype='GROUND') or
         (LEVEL.LevelItemDefinition.item[LevelItemListBox.ItemIndex].itemtype='CLEAN')) then self.chk_road.Checked:=true;
         
     if ((LEVEL.LevelItemDefinition.item[LevelItemListBox.ItemIndex].itemtype='OBSTACLE')  or
         (LEVEL.LevelItemDefinition.item[LevelItemListBox.ItemIndex].itemtype='BRIDGE'))then self.chk_obstacle.Checked:=true;
     
     if (LEVEL.LevelItemDefinition.item[LevelItemListBox.ItemIndex].itemtype='DECOR64')then self.chk_decor64.Checked:=true;
     
     if (LEVEL.LevelItemDefinition.item[LevelItemListBox.ItemIndex].itemtype='DECOR16')then
     begin
          self.chk_decor.Checked:=true;
          cursor_mode:=1;
     end;

end;
// *****************************************************************************
// MAIN:
// *****************************************************************************
procedure Tfrm_main.LevelPaintBoxClick(Sender: TObject);
begin
//    self.UpdateLevel();
end;
// *****************************************************************************
// MAIN:
// *****************************************************************************
procedure Tfrm_main.LevelPaintBoxMouseDown(Sender: TObject;
  Button: TMouseButton; Shift: TShiftState; X, Y: Integer);
begin
  if LEVEL.Flags.bDefinition=false then exit;

  if ((Button=MBLEFT) and (ssShift in shift)) then
  begin
       LEVEL.SetCellDRV(x div 64,y div 64);
       exit;
  end;
  
  if (Button=MBLEFT) then
  begin
       LEVEL.mouse_pos.x:=x div 64;
       LEVEL.mouse_pos.y:=y div 64;

       LEVEL.mouse_SUB_pos.x:=x div 16;
       LEVEL.mouse_SUB_pos.y:=y div 16;

       LEVEL.SetCell(x div 64,y div 64,lbl_sel_name.Caption,SelectedItemID);
       

       if (cursor_mode=1) then
       begin
            LEVEL.SetSubCell(x div 64,y div 64,(LEVEL.mouse_SUB_pos.x) mod 4, (LEVEL.mouse_SUB_pos.y) mod 4,lbl_sel_name.Caption,SelectedItemID);
            

       end;

  end;


  if button = mbleft then lm_button:=1;
  if button = mbright then rm_button:=1;
  
end;

// *****************************************************************************
// MAIN:
// *****************************************************************************

procedure Tfrm_main.LevelPaintBoxMouseMove(Sender: TObject; Shift: TShiftState; X,Y: Integer);
begin


    LEVEL.mouse_pos.x:=x div 64;
    LEVEL.mouse_pos.y:=y div 64;

    LEVEL.mouse_SUB_pos.x:=x div 16;
    LEVEL.mouse_SUB_pos.y:=y div 16;


    if lm_button=1 then
    begin


         if (cursor_mode=1) then
             LEVEL.SetSubCell(x div 64,y div 64,(LEVEL.mouse_SUB_pos.x) mod 4, (LEVEL.mouse_SUB_pos.y) mod 4,lbl_sel_name.Caption,SelectedItemID)
         else
              LEVEL.SetCell(x div 64,y div 64,lbl_sel_name.Caption,SelectedItemID);

    end;



//    self.UpdateLevel();

end;
// *****************************************************************************
// MAIN:
// *****************************************************************************
procedure Tfrm_main.LevelPaintBoxMouseUp(Sender: TObject; Button: TMouseButton;
  Shift: TShiftState; X, Y: Integer);
begin
 lm_button:=0;
 rm_button:=0;
end;

procedure Tfrm_main.MenuItem11Click(Sender: TObject);
var _name:String;
begin
     if LEVEL.Flags.bDefinition=false then exit;
  // DELETE ALL
  _name:=frm_main.LEVEL.LevelItemDefinition.item[0].name;
  if (cursor_mode=1) then
     LEVEL.SetSubCell(LEVEL.mouse_pos.x,LEVEL.mouse_pos.y,(LEVEL.mouse_SUB_pos.x) mod 4, (LEVEL.mouse_SUB_pos.y) mod 4,_name,0)
  else
     LEVEL.SetCell(LEVEL.mouse_pos.x,LEVEL.mouse_pos.y,_name,0);
     self.DrawMapGrid();
end;

procedure Tfrm_main.MenuItem12Click(Sender: TObject);
var _name:String;
begin
     if LEVEL.Flags.bDefinition=false then exit;
     // DELETE ROAD
     LEVEL.cell[LEVEL.mouse_pos.x+LEVEL.view_pos.x,LEVEL.mouse_pos.y+LEVEL.view_pos.y].item_road_id:=0;
     self.DrawMapGrid();
end;

procedure Tfrm_main.MenuItem13Click(Sender: TObject);
begin
     if LEVEL.Flags.bDefinition=false then exit;
       // DELETE OBSATCLE
     LEVEL.cell[LEVEL.mouse_pos.x+LEVEL.view_pos.x,LEVEL.mouse_pos.y+LEVEL.view_pos.y].item_obst_id:=-1;
     self.DrawMapGrid();
end;

procedure Tfrm_main.MenuItem9Click(Sender: TObject);
begin
 if LEVEL.Flags.bDefinition=false then exit;
       // DELETE DECOR64
     LEVEL.cell[LEVEL.mouse_pos.x+LEVEL.view_pos.x,LEVEL.mouse_pos.y+LEVEL.view_pos.y].item_dec64_id:=-1;
     self.DrawMapGrid();
end;

procedure Tfrm_main.MenuItem14Click(Sender: TObject);
begin
     if LEVEL.Flags.bDefinition=false then exit;
     // DELETE DECOR16
     LEVEL.cell[LEVEL.mouse_pos.x+LEVEL.view_pos.x,LEVEL.mouse_pos.y+LEVEL.view_pos.y].item_decor_array[(LEVEL.mouse_SUB_pos.x) mod 4, (LEVEL.mouse_SUB_pos.y) mod 4].ID:=-1;
     self.DrawMapGrid();
end;

procedure Tfrm_main.MenuItem15Click(Sender: TObject);
var _name:String;
begin
  // CUT CELL
  bTMP_CELL:=true;
  TMP_CELL:=LEVEL.GetAllCell();
  self.MenuItem17.Enabled:=true;
if LEVEL.Flags.bDefinition=false then exit;
  // DELETE ALL
  _name:=frm_main.LEVEL.LevelItemDefinition.item[0].name;
  if (cursor_mode=1) then
     LEVEL.SetSubCell(LEVEL.mouse_pos.x,LEVEL.mouse_pos.y,(LEVEL.mouse_SUB_pos.x) mod 4, (LEVEL.mouse_SUB_pos.y) mod 4,_name,0)
  else
     LEVEL.SetCell(LEVEL.mouse_pos.x,LEVEL.mouse_pos.y,_name,0);
     self.DrawMapGrid();
end;

procedure Tfrm_main.MenuItem16Click(Sender: TObject);
begin
  bTMP_CELL:=true;
  TMP_CELL:=LEVEL.GetAllCell();
  self.MenuItem17.Enabled:=true;
end;

procedure Tfrm_main.MenuItem17Click(Sender: TObject);
begin
  LEVEL.SetAllCell(TMP_CELL);
  self.DrawMapGrid();
end;

procedure Tfrm_main.MenuItem18Click(Sender: TObject);
var mx,my:integer;
    del_drv:integer;
begin

     if (LEVEL.cell[level.mouse_pos.x+level.view_pos.x,level.mouse_pos.y+level.view_pos.y].drv_id=-1) then exit;

     if (LEVEL.cell[level.mouse_pos.x+level.view_pos.x,level.mouse_pos.y+level.view_pos.y].drv_id_top>0) then
     begin
        del_drv:= LEVEL.cell[level.mouse_pos.x+level.view_pos.x,level.mouse_pos.y+level.view_pos.y].drv_id_top;
     
        LEVEL.drv_id_count:=del_drv;

        for mx:=0 to LEVEL.size.x-1 do
        for my:=0 to LEVEL.size.y-1 do
        begin
             if (LEVEL.cell[mx,my].drv_id_top>=del_drv) then LEVEL.cell[mx,my].drv_id_top:=-1;
             if (LEVEL.cell[mx,my].drv_id>=del_drv) then LEVEL.cell[mx,my].drv_id:=-1;
         end;
     end
     else
     begin
         del_drv:= LEVEL.cell[level.mouse_pos.x+level.view_pos.x,level.mouse_pos.y+level.view_pos.y].drv_id;
         LEVEL.drv_id_count:=del_drv;

        for mx:=0 to LEVEL.size.x-1 do
        for my:=0 to LEVEL.size.y-1 do
        begin

             if (LEVEL.cell[mx,my].drv_id>=del_drv) then
             begin
                  if (LEVEL.cell[mx,my].drv_id_top>=del_drv) then LEVEL.cell[mx,my].drv_id_top:=-1;
                  if (LEVEL.cell[mx,my].drv_id>=del_drv) then LEVEL.cell[mx,my].drv_id:=-1;
             end;
         end;

     end;

     DrawMapGridFull();
end;



// *****************************************************************************
// MAIN:
// *****************************************************************************

procedure Tfrm_main.MenuItem3Click(Sender: TObject);
begin
  LevelItemListBox.Clear();
  frm_new_level.showmodal();
  IconScrollBar.Position:=0;
  frm_main.DrawMapGridFull();

end;

procedure Tfrm_main.MenuItem4Click(Sender: TObject);
begin

  OpenDialogPrj.Execute();
  
  if Length(OpenDialogPrj.FileName)=0 then exit;
  
  LoadProject(OpenDialogPrj.FileName);
end;

// *****************************************************************************
// MAIN:
// *****************************************************************************
procedure Tfrm_main.MenuItem5Click(Sender: TObject);
begin
  SaveData();
end;

procedure Tfrm_main.MenuItem6Click(Sender: TObject);
begin
  SaveDialogPrj.Execute();
  if Length(SaveDialogPrj.FileName)=0 then exit;
  
  
  LEVEL.project_name:=SaveDialogPrj.FileName;
  self.Caption:='STKed 2008 - ['+LEVEL.project_name+']';
  SaveData();
  self.MenuItem5.Enabled:=true;
  
  
end;

procedure Tfrm_main.MenuItem7Click(Sender: TObject);
var prj_name:String;
    p:integer;
begin

  frm_export_track.ShowModal();

  
end;

// *****************************************************************************
// MAIN:
// *****************************************************************************
procedure Tfrm_main.MenuItem8Click(Sender: TObject);
begin
  close();
end;


// *****************************************************************************
// MAIN:
// *****************************************************************************
procedure Tfrm_main.ScrollBar_x_cellChange(Sender: TObject);
begin
  LEVEL.view_pos.X:=self.ScrollBar_x_cell.Position;
self.DrawMapGridFull();
end;
// *****************************************************************************
// MAIN:
// *****************************************************************************
procedure Tfrm_main.ScrollBar_x_cellScroll(Sender: TObject;
  ScrollCode: TScrollCode; var ScrollPos: Integer);
begin
self.DrawMapGridFull();
end;
// *****************************************************************************
// MAIN:
// *****************************************************************************
procedure Tfrm_main.ScrollBar_y_cellChange(Sender: TObject);
begin
  LEVEL.view_pos.Y:=self.ScrollBar_y_cell.Position;
  self.DrawMapGridFull();
end;
// *****************************************************************************
// MAIN:
// *****************************************************************************
procedure Tfrm_main.ScrollBar_y_cellScroll(Sender: TObject;
  ScrollCode: TScrollCode; var ScrollPos: Integer);
begin
  self.DrawMapGridFull();
end;

procedure Tfrm_main.Timer1Timer(Sender: TObject);
begin
  self.UpdateLevel();
end;

// *****************************************************************************
// MAIN:
// *****************************************************************************
procedure Tfrm_main.DrawMapGrid();
var
   x,sx:integer;
    y,sy:integer;
    img_road_id:integer;
    img_obstacle_id:integer;
    img_decor_id:integer;
    img_dec16_id:integer;
    drv_id:Integer;
    img_drv_id:integer;
    img_drv_id_top:integer;
    
begin
     if LEVEL.Flags.bDefinition=false then exit;
     // draw map
     //for x:=0 to 9 do
     //for y:=0 to 9 do
     x:=LEVEL.mouse_pos.x;
     y:=LEVEL.mouse_pos.y;
     begin
          img_road_id:=LEVEL.GetCell(x,y,'ROAD');
          img_obstacle_id:=LEVEL.GetCell(x,y,'OBSTACLE');
          img_dec16_id:=LEVEL.GetCell(x,y,'DECOR64');
          img_drv_id :=LEVEL.GetCellDRV(x,y,'BOTTOM');
          img_drv_id_top :=LEVEL.GetCellDRV(x,y,'TOP');

          if (img_road_id=-1) then
             self.Image1.Canvas.Draw(x*64,y*64,img_none.Picture.Graphic)
          else
              self.Image1.Canvas.Draw(x*64,y*64,LEVEL.LevelItemDefinition.item[img_road_id].image_data.Picture.Graphic);

          if (img_obstacle_id<>-1) then
             self.Image1.Canvas.Draw(x*64,y*64,LEVEL.LevelItemDefinition.item[img_obstacle_id].image_data.Picture.Graphic);

          if (img_dec16_id<>-1) then
             self.Image1.Canvas.Draw(x*64,y*64,LEVEL.LevelItemDefinition.item[img_dec16_id].image_data.Picture.Graphic);

          for sx:=0 to MAX_SUB_SIZE-1 do
          for sy:=0 to MAX_SUB_SIZE-1 do
          begin
                img_decor_id:=LEVEL.GetSubCell(x,y,sx,sy,'DECOR16');
                if (img_decor_id<>-1) then
                begin
                     self.Image1.Canvas.Draw(x*64+(sx*16),y*64+(sy*16),LEVEL.LevelItemDefinition.item[img_decor_id].image_data.Picture.Graphic);
                end;
                
          end;
          
          self.Image1.Canvas.Brush.Style := bsclear;
          self.Image1.Canvas.Font.Style:=[fsBold];
          if ((img_drv_id<>-1) and (chk_drv_num.checked)) then
          begin

               self.Image1.Canvas.Font.Color  := clBlack;
               self.Image1.Canvas.TextOut(x*64+8,y*64+(64-16),IntToStr(img_drv_id));
               self.Image1.Canvas.Font.Color  := clRed;
               self.Image1.Canvas.TextOut(x*64+8-1,y*64+(64-16)-1,IntToStr(img_drv_id));
          end;
          if ((img_drv_id_top<>-1) and (chk_drv_num.checked)) then
          begin
               self.Image1.Canvas.Font.Color  := clBlack;
               self.Image1.Canvas.TextOut(x*64+8,y*64,IntToStr(img_drv_id_top));
               self.Image1.Canvas.Font.Color  := clYellow;
               self.Image1.Canvas.TextOut(x*64+8-1,y*64-1,IntToStr(img_drv_id_top));
          end;

     end;
end;



procedure Tfrm_main.DrawMapGridFull();
var
   x,sx:integer;
    y,sy:integer;
    img_road_id:integer;
    img_obstacle_id:integer;
    img_decor_id:integer;
    img_dec16_id:integer;
    img_drv_id:integer;
    img_drv_id_top:integer;
begin
     if LEVEL.Flags.bDefinition=false then exit;
     
     // draw map
     for x:=0 to 9 do
     for y:=0 to 9 do

     begin
          img_road_id:=LEVEL.GetCell(x,y,'ROAD');
          img_obstacle_id:=LEVEL.GetCell(x,y,'OBSTACLE');
          img_dec16_id:=LEVEL.GetCell(x,y,'DECOR64');
          img_drv_id :=LEVEL.GetCellDRV(x,y,'BOTTOM');
          img_drv_id_top :=LEVEL.GetCellDRV(x,y,'TOP');

          if (img_road_id=-1) then
             self.Image1.Canvas.Draw(x*64,y*64,img_none.Picture.Graphic)
          else
              self.Image1.Canvas.Draw(x*64,y*64,LEVEL.LevelItemDefinition.item[img_road_id].image_data.Picture.Graphic);

          if (img_obstacle_id<>-1) then
             self.Image1.Canvas.Draw(x*64,y*64,LEVEL.LevelItemDefinition.item[img_obstacle_id].image_data.Picture.Graphic);

          if (img_dec16_id<>-1) then
             self.Image1.Canvas.Draw(x*64,y*64,LEVEL.LevelItemDefinition.item[img_dec16_id].image_data.Picture.Graphic);


          for sx:=0 to MAX_SUB_SIZE-1 do
          for sy:=0 to MAX_SUB_SIZE-1 do
          begin
                img_decor_id:=LEVEL.GetSubCell(x,y,sx,sy,'DECOR16');
                if (img_decor_id<>-1) then
                begin
                     self.Image1.Canvas.Draw(x*64+(sx*16),y*64+(sy*16),LEVEL.LevelItemDefinition.item[img_decor_id].image_data.Picture.Graphic);
                     

                end;

          end;
          
          self.Image1.Canvas.Brush.Style := bsclear;
          self.Image1.Canvas.Font.Style:=[fsBold];

          if ((img_drv_id<>-1) and (chk_drv_num.checked)) then
          begin
               self.Image1.Canvas.Font.Color  := clBlack;
               self.Image1.Canvas.TextOut(x*64+8,y*64+(64-16),IntToStr(img_drv_id));
               self.Image1.Canvas.Font.Color  := clRed;
               self.Image1.Canvas.TextOut(x*64+8-1,y*64+(64-16)-1,IntToStr(img_drv_id));
          end;
          
          if ((img_drv_id_top<>-1) and (chk_drv_num.checked)) then
          begin
               self.Image1.Canvas.Font.Color  := clBlack;
               self.Image1.Canvas.TextOut(x*64+8,y*64,IntToStr(img_drv_id_top));
               self.Image1.Canvas.Font.Color  := clYellow;
               self.Image1.Canvas.TextOut(x*64+8-1,y*64-1,IntToStr(img_drv_id_top));
          end;


     end;
end;

// *****************************************************************************
// MAIN:
// *****************************************************************************
procedure Tfrm_main.DrawMapCursor();
var a,b,c,d:TPoint;
begin

     //exit;

     if (cursor_mode=0) then
     begin
     a.x:=((LEVEL.mouse_pos.x)*64);
     a.y:=((LEVEL.mouse_pos.y)*64);
     b.x:=((LEVEL.mouse_pos.x)*64)+64;
     b.y:=((LEVEL.mouse_pos.y)*64);
     c.x:=((LEVEL.mouse_pos.x)*64)+64;
     c.y:=((LEVEL.mouse_pos.y)*64)+64;
     d.x:=((LEVEL.mouse_pos.x)*64);
     d.y:=((LEVEL.mouse_pos.y)*64)+64;


     self.LevelPaintBox.Canvas.pen.Color:=$FFFFFF;

     self.LevelPaintBox.Canvas.Line(a.x,a.y,b.x,b.y);
     self.LevelPaintBox.Canvas.Line(b.x,b.y,c.x,c.y);
     self.LevelPaintBox.Canvas.Line(c.x,c.y,d.x,d.y);
     self.LevelPaintBox.Canvas.Line(d.x,d.y,a.x,a.y);
     end;

     if (cursor_mode=1) then
     begin

          a.x:=((LEVEL.mouse_SUB_pos.x)*16);
          a.y:=((LEVEL.mouse_SUB_pos.y)*16);
          b.x:=((LEVEL.mouse_SUB_pos.x)*16)+16;
          b.y:=((LEVEL.mouse_SUB_pos.y)*16);
          c.x:=((LEVEL.mouse_SUB_pos.x)*16)+16;
          c.y:=((LEVEL.mouse_SUB_pos.y)*16)+16;
          d.x:=((LEVEL.mouse_SUB_pos.x)*16);
          d.y:=((LEVEL.mouse_SUB_pos.y)*16)+16;


          self.LevelPaintBox.Canvas.pen.Color:=$FF00FF;

          self.LevelPaintBox.Canvas.Line(a.x,a.y,b.x,b.y);
          self.LevelPaintBox.Canvas.Line(b.x,b.y,c.x,c.y);
          self.LevelPaintBox.Canvas.Line(c.x,c.y,d.x,d.y);
          self.LevelPaintBox.Canvas.Line(d.x,d.y,a.x,a.y);
     
     end;

end;
// *****************************************************************************
// MAIN:
// *****************************************************************************
procedure Tfrm_main.UpdateLevel();
var
    img_road_id:integer;
    img_obstacle_id:integer;
begin

    if LEVEL.Flags.bDefinition=false then exit;

    inc(counter);


    LEVEL.real_pos.x := LEVEL.view_pos.x + LEVEL.mouse_pos.x;
    LEVEL.real_pos.y := LEVEL.view_pos.y + LEVEL.mouse_pos.y;

    img_road_id:=LEVEL.GetCell(LEVEL.real_pos.x,LEVEL.real_pos.y,'ROAD');
    img_obstacle_id:=LEVEL.GetCell(LEVEL.real_pos.x,LEVEL.real_pos.y,'OBSTACLE');


    self.LevelPaintBox.Canvas.Draw(0,0,Image1.Picture.Graphic);
    self.DrawMapGrid();


//    label2.caption:='MAP  [x,y]='+IntToStr(LEVEL.view_pos.x)+','+IntToStr(LEVEL.view_pos.y);
//    label3.caption:='MOUSE[x,y]='+IntToStr(LEVEL.mouse_pos.x)+','+IntToStr(LEVEL.mouse_pos.y);
//    label4.caption:='GRID [x,y]='+IntToStr(LEVEL.real_pos.x)+','+IntToStr(LEVEL.real_pos.y);
//    label5.caption:='ROAD ID: ='+IntToStr(img_road_id);
//    label6.caption:='OBST ID: ='+IntToStr(img_obstacle_id);
//    label7.caption:='SUB [x,y]='+IntToStr((LEVEL.mouse_SUB_pos.x) mod 4)+','+IntToStr((LEVEL.mouse_SUB_pos.y)mod 4);
    
    DrawMapCursor();
    
end;

procedure Tfrm_main.UpdateIconsByScrollBar();
var i,img_id:integer;
    img_map:String;
    img:TComponent;
begin
     for i:=0 to 11 do
     begin
          img:=self.FindComponent('item_image_'+IntToStr(i+1));
          img_id:=((img as TImage).Tag)+self.IconScrollBar.Position;
          img_map:='editor/icons/'+LEVEL.LevelItemDefinition.item[img_id].image_file;
          (img as TImage).Picture.LoadFromFile(img_map);
          (img as TImage).Hint:=LEVEL.LevelItemDefinition.item[img_id].name+'['+LEVEL.LevelItemDefinition.item[img_id].ItemType+']';
          (img as TImage).showhint:=true;
     end;
end;

initialization
  {$I main.lrs}

end.

