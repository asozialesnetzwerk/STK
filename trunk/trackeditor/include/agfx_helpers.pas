unit agfx_helpers;

{$mode objfpc}{$H+}

interface



uses
  Classes, SysUtils,agfx_types;

  function GetRotatedDRV(V:TF3D_Vector2f;angle:integer):TF3D_Vector2f;


implementation

function GetRotatedDRV(V:TF3D_Vector2f;angle:integer):TF3D_Vector2f;
var res:TF3D_Vector2f;
begin

     if angle=90 then
     begin
          res:=v;
     end;

     if angle=90 then
     begin
          res.x:=v.y;
          res.y:=-v.x;
     end;

     if angle=180 then
     begin
          res.x:=-v.x;
          res.y:=-v.y;
     end;

     if angle=270 then
     begin
          res.x:=-v.y;
          res.y:=-v.x;
     end;

     result:=res;
end;

end.

