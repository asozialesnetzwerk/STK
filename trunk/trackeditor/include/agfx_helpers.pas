unit agfx_helpers;

{$mode objfpc}{$H+}

interface



uses
  Classes, SysUtils,agfx_types;

  function GetRotatedDRV(V:TF3D_Vector3f;angle:single):TF3D_Vector3f;


implementation

function GetRotatedDRV(V:TF3D_Vector3f;angle:single):TF3D_Vector3f;
var res:TF3D_Vector3f;
begin

     if angle=90 then
     begin
          res:=v;
     end;

     if angle=90 then
     begin
          res.x:=v.y;
          res.y:=-v.x;
          res.z:=v.z;
     end;

     if angle=180 then
     begin
          res.x:=-v.x;
          res.y:=-v.y;
          res.z:=v.z;
     end;

     if angle=270 then
     begin
          res.x:=-v.y;
          res.y:=-v.x;
          res.z:=v.z;
     end;

     result:=res;
end;

end.

