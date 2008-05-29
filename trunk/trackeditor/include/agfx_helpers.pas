unit agfx_helpers;

{$mode objfpc}{$H+}

interface



uses
  Classes, SysUtils,agfx_types;

type TDRVLINE = record
     L:TF3D_Vector3f;
     R:TF3D_Vector3f;
     end;

  function GetRotatedDRV(V:TF3D_Vector3f;angle:single):TF3D_Vector3f;
  function IsWayInThisDir(P,O,N:TF3D_Vector2i;R1x,R1y,R2x,R2y:integer):boolean;
  function AnalyzeDirection(P,O,N:TF3D_Vector2i;width:single):TDRVLINE;
implementation

function GetRotatedDRV(V:TF3D_Vector3f;angle:single):TF3D_Vector3f;
var res:TF3D_Vector3f;
begin

     if angle=0 then
     begin
          res:=v;
     end;

     if angle=90 then
     begin
          res.x:=v.y;
          res.y:=-v.x;
          res.z:=v.z;
     end;

     if ((angle=180) or  (angle=-180)) then
     begin
          res.x:=-v.x;
          res.y:=-v.y;
          res.z:=v.z;
     end;

     if ((angle=270) or (angle=-90)) then
     begin
          res.x:=-v.y;
          res.y:=v.x;
          res.z:=v.z;
     end;

     result:=res;
end;


function IsWayInThisDir(P,O,N:TF3D_Vector2i;R1x,R1y,R2x,R2y:integer):boolean;
var _R1x,_R1y,_R2x,_R2y:integer;
    res:boolean;
begin

     res:=false;
     
    _R1x := O.x-N.x;
    _R1y := O.y-N.Y;
    _R2x := O.x-P.x;
    _R2y := O.y-P.Y;
    
     if ((_R1x=R1x) and (_R1y=R1y) and (_R2x=R2x) and (_R2y=R2y)) then res:=true;
    
    result:=res;
end;


function AnalyzeDirection(P,O,N:TF3D_Vector2i;width:single):TDRVLINE;
var res:TDRVLINE;
begin

     res.L.X:=9999;
     res.L.Y:=9999;
     res.R.X:=9999;
     res.R.Y:=9999;
     
     // [A]
     if IsWayInThisDir(P,O,N,0,1,0,-1) then
     begin
          res.L.X  :=-1*width;
          res.L.Y  := 0;
          res.R.X := 1*width;
          res.R.Y := 0;
     end;
     
     // [B]
     if IsWayInThisDir(P,O,N,0,-1,0,1) then
     begin
          res.L.X  := 1*width;
          res.L.Y  := 0;
          res.R.X :=-1*width;
          res.R.Y := 0;
     end;
     
     // [C]
     if IsWayInThisDir(P,O,N,-1,0,1,0) then
     begin
          res.L.X  := 0;
          res.L.Y  := 1*width;
          res.R.X := 0;
          res.R.Y :=-1*width;
     end;

     // [D]
     if IsWayInThisDir(P,O,N,1,0,-1,0) then
     begin
          res.L.X  := 0;
          res.L.Y  :=-1*width;
          res.R.X := 0;
          res.R.Y := 1*width;
     end;
     
     // [E]
     if IsWayInThisDir(P,O,N,0,-1,-1,0) then
     begin
          res.L.X  := 1*width;
          res.L.Y  :=-1*width;
          res.R.X :=-1*width;
          res.R.Y := 1*width;
     end;
     
     // [F]
     if IsWayInThisDir(P,O,N,0,1,1,0) then
     begin
          res.L.X  :=-1*width;
          res.L.Y  := 1*width;
          res.R.X := 1*width;
          res.R.Y :=-1*width;
     end;

     // [G]
     if IsWayInThisDir(P,O,N,1,0,0,-1) then
     begin
          res.L.X  :=-1*width;
          res.L.Y  :=-1*width;
          res.R.X := 1*width;
          res.R.Y := 1*width;
     end;

     // [H]
     if IsWayInThisDir(P,O,N,-1,0,0,1) then
     begin
          res.L.X  := 1*width;
          res.L.Y  := 1*width;
          res.R.X :=-1*width;
          res.R.Y :=-1*width;
     end;
     
     // [I]
     if IsWayInThisDir(P,O,N,-1,0,0,-1) then
     begin
          res.L.X  :=-1*width;
          res.L.Y  := 1*width;
          res.R.X := 1*width;
          res.R.Y :=-1*width;
     end;
     
     // [J]
     if IsWayInThisDir(P,O,N,1,0,0,1) then
     begin
          res.L.X  := 1*width;
          res.L.Y  :=-1*width;
          res.R.X :=-1*width;
          res.R.Y := 1*width;
     end;
     
     // [K]
     if IsWayInThisDir(P,O,N,0,-1,1,0) then
     begin
          res.L.X  := 1*width;
          res.L.Y  := 1*width;
          res.R.X :=-1*width;
          res.R.Y :=-1*width;
     end;
     
     // [L]
     if IsWayInThisDir(P,O,N,0,1,-1,0) then
     begin
          res.L.X  :=-1*width;
          res.L.Y  :=-1*width;
          res.R.X := 1*width;
          res.R.Y := 1*width;
     end;

     result:=res;
end;

end.

