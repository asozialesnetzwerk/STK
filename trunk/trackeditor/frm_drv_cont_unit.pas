unit frm_drv_cont_unit;

{$mode objfpc}{$H+}

interface

uses
  Classes, SysUtils, LResources, Forms, Controls, Graphics, Dialogs, StdCtrls;

type

  { Tfrm_drv_cont }

  Tfrm_drv_cont = class(TForm)
    Button1: TButton;
    Button2: TButton;
    Button3: TButton;
    Label1: TLabel;
    procedure Button1Click(Sender: TObject);
    procedure Button2Click(Sender: TObject);
    procedure Button3Click(Sender: TObject);
  private
    { private declarations }
  public
    { public declarations }
  end; 

var
  frm_drv_cont: Tfrm_drv_cont;

implementation
uses main;

{ Tfrm_drv_cont }

procedure Tfrm_drv_cont.Button3Click(Sender: TObject);
begin
  frm_main.LEVEL.dst_drv_layer:=-1;
  close();
end;

procedure Tfrm_drv_cont.Button2Click(Sender: TObject);
begin
    frm_main.LEVEL.dst_drv_layer:=1;
  close();
end;

procedure Tfrm_drv_cont.Button1Click(Sender: TObject);
begin
    frm_main.LEVEL.dst_drv_layer:=0;
  close();
end;

initialization
  {$I frm_drv_cont_unit.lrs}

end.

