unit frm_stked_about_unit;

{$mode objfpc}{$H+}

interface

uses
  Classes, SysUtils, LResources, Forms, Controls, Graphics, Dialogs, ExtCtrls;

type

  { Tfrm_about }

  Tfrm_about = class(TForm)
    Image1: TImage;
    procedure Image1DblClick(Sender: TObject);
  private
    { private declarations }
  public
    { public declarations }
  end; 

var
  frm_about: Tfrm_about;

implementation

{ Tfrm_about }

procedure Tfrm_about.Image1DblClick(Sender: TObject);
begin
  close();
end;

initialization
  {$I frm_stked_about_unit.lrs}

end.

