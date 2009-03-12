unit frm_EportDone_unit;

{$mode objfpc}{$H+}

interface

uses
  Classes, SysUtils, LResources, Forms, Controls, Graphics, Dialogs, StdCtrls;

type

  { Tfrm_ExportDone }

  Tfrm_ExportDone = class(TForm)
    Button1: TButton;
    procedure Button1Click(Sender: TObject);
  private
    { private declarations }
  public
    { public declarations }
  end; 

var
  frm_ExportDone: Tfrm_ExportDone;

implementation

{ Tfrm_ExportDone }

procedure Tfrm_ExportDone.Button1Click(Sender: TObject);
begin
  close();
end;

initialization
  {$I frm_eportdone_unit.lrs}

end.

