unit frm_new;

{$mode objfpc}{$H+}

interface

uses
  Classes, SysUtils, LResources, Forms, Controls, Graphics, Dialogs, StdCtrls;

type

  { Tfrm_new_level }

  Tfrm_new_level = class(TForm)
    Button1: TButton;
    Button2: TButton;
    ComboBox1: TComboBox;
    ed_prj_name: TEdit;
    Label1: TLabel;
    Label2: TLabel;
    Label3: TLabel;
    Label4: TLabel;
    Label5: TLabel;
    Label6: TLabel;
    sb_size_x: TScrollBar;
    sb_size_y: TScrollBar;
    procedure Button1Click(Sender: TObject);
    procedure Button2Click(Sender: TObject);
    procedure FormShow(Sender: TObject);
    procedure sb_size_xChange(Sender: TObject);
    procedure sb_size_yChange(Sender: TObject);
  private
    { private declarations }
  public
    { public declarations }
  end; 

var
  frm_new_level: Tfrm_new_level;

implementation
uses main;
{ Tfrm_new_level }

// *****************************************************************************
// Create Level
// *****************************************************************************
procedure Tfrm_new_level.Button2Click(Sender: TObject);
var i:integer;
begin
  if length(combobox1.text)=0 then
  begin
      exit();
  end;
  frm_main.LEVEL.LevelItemDefinition.LoadFromFile('editor/definitions/'+Combobox1.text);
  frm_main.LEVEL.Flags.bDefinition:=true;
  frm_main.LEVEL.size.X:=sb_size_x.position;
  frm_main.LEVEL.size.Y:=sb_size_y.position;
  frm_main.LEVEL.view_pos.X:=0;
  frm_main.LEVEL.view_pos.Y:=0;
  frm_main.LEVEL.project_name:=ed_prj_name.text+'.prj';
  frm_main.LEVEL.def_file_name:=Combobox1.text;
  frm_main.LEVEL.DrvL_List.Clear;
  frm_main.LEVEL.DrvR_List.Clear;
  
  frm_main.Caption:='STKed 2008 - ['+frm_main.LEVEL.project_name+']';
  frm_main.LEVEL.ClearGrid();
  
  
  frm_main.IconScrollBar.Position:=0;
  frm_main.IconScrollBar.Min:=0;
  frm_main.IconScrollBar.Max:=frm_main.LEVEL.LevelItemDefinition.count-20;
  
  frm_main.UpdateIconsByScrollBar();
  
  for i:=0 to frm_main.LEVEL.LevelItemDefinition.count-1 do
  begin
       frm_main.LevelItemListBox.Items.Add(frm_main.LEVEL.LevelItemDefinition.item[i].name);
  end;
  
  
  frm_main.UpdateLevel();
  
  frm_main.ScrollBar_x_cell.Max:=frm_main.LEVEL.size.X-10;
  frm_main.ScrollBar_y_cell.Max:=frm_main.LEVEL.size.y-10;
  frm_main.LevelItemListBox.Selected[0]:=true;
  frm_main.LevelItemListBox.OnClick(self);
  frm_main.MenuItem6.Enabled:=true;
  frm_main.MenuItem7.Enabled:=true;

  
  
  close();
end;

// *****************************************************************************
// On Show
// *****************************************************************************
procedure Tfrm_new_level.FormShow(Sender: TObject);
var i:integer;
begin
     combobox1.Items.Clear;
     for i:=0 to 9 do
     begin
          if frm_main.LEVEL.config.DEF_FILE_LIST[i]<>'none' then combobox1.Items.Add(frm_main.LEVEL.config.DEF_FILE_LIST[i]);
     end;
    combobox1.text:=combobox1.Items[0];
end;

// *****************************************************************************
// set level width
// *****************************************************************************
procedure Tfrm_new_level.sb_size_xChange(Sender: TObject);
begin
     label4.caption:=IntToStr(sb_size_x.position);
end;

// *****************************************************************************
// set level height
// *****************************************************************************
procedure Tfrm_new_level.sb_size_yChange(Sender: TObject);
begin
  label5.caption:=IntToStr(sb_size_y.position);
end;

// *****************************************************************************
// cancel
// *****************************************************************************
procedure Tfrm_new_level.Button1Click(Sender: TObject);
begin
  close();
end;

initialization
  {$I frm_new.lrs}

end.

