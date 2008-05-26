unit frm_exp_track_unit;

{$mode objfpc}{$H+}

interface

uses
  Classes, SysUtils, LResources, Forms, Controls, Graphics, Dialogs, EditBtn,
  save_prj,
  StdCtrls;

type

  { Tfrm_export_track }

  Tfrm_export_track = class(TForm)
    Button1: TButton;
    Button2: TButton;
    CheckBox1: TCheckBox;
    CheckBox2: TCheckBox;
    CheckBox3: TCheckBox;
    CheckBox4: TCheckBox;
    CheckBox5: TCheckBox;
    chk_drv_debug: TCheckBox;
    DirectoryEdit1: TDirectoryEdit;
    Label1: TLabel;
    procedure Button1Click(Sender: TObject);
    procedure Button2Click(Sender: TObject);
  private
    { private declarations }
  public
    { public declarations }
  end; 

var
  frm_export_track: Tfrm_export_track;

implementation
uses main;
{ Tfrm_export_track }

procedure Tfrm_export_track.Button1Click(Sender: TObject);
var prj_name:String;
    p:integer;
begin
  if length(DirectoryEdit1.Text)=0 then exit;
  
  frm_main.LEVEL.COnfig.bDRVR:=CheckBox1.Checked;
  frm_main.LEVEL.COnfig.bDRVL:=CheckBox2.Checked;
  frm_main.LEVEL.COnfig.bLOC:=CheckBox3.Checked;
  frm_main.LEVEL.COnfig.bTRACK:=CheckBox4.Checked;
  frm_main.LEVEL.COnfig.bHERRING:=CheckBox5.Checked;
  frm_main.LEVEL.COnfig.bDRVDEB:=chk_drv_debug.Checked;
  
  frm_main.LEVEL.COnfig.export_path:=DirectoryEdit1.Text;
  
  prj_name:=ExtractFileNAme(frm_main.LEVEL.project_name);
  p := pos('.',prj_name);
  if p>0 then prj_name:=copy(prj_name,0,p-1);

  ExportLevel(prj_name);
  
  close();
end;

procedure Tfrm_export_track.Button2Click(Sender: TObject);
begin
  close();
end;

initialization
  {$I frm_exp_track_unit.lrs}

end.

