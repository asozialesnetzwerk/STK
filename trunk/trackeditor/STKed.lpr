program STKed;

{$mode objfpc}{$H+}

uses
  {$IFDEF UNIX}{$IFDEF UseCThreads}
  cthreads,
  {$ENDIF}{$ENDIF}
  Interfaces, // this includes the LCL widgetset
  Forms
  { you can add units after this }, main, AGFX_definition_class, AGFX_GLOBALS,
  agfx_leveldesign_class, frm_new, save_prj, agfx_config, frm_EportDone_unit,
  frm_exp_track_unit, agfx_helpers;

begin
  Application.Title:='STKed';
  Application.Initialize;
  Application.CreateForm(Tfrm_main, frm_main);
  Application.CreateForm(Tfrm_new_level, frm_new_level);
  Application.CreateForm(Tfrm_ExportDone, frm_ExportDone);
  Application.CreateForm(Tfrm_export_track, frm_export_track);
  Application.Run;
end.

