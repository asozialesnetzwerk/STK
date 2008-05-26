unit AGFX_definition_class;
// *****************************************************************************
//
// *****************************************************************************

{$mode objfpc}{$H+}

interface

uses
  Classes, SysUtils, ExtCtrls,agfx_types,agfx_parser,Graphics;

// *****************************************************************************
//  LEVEL ITEM
// *****************************************************************************

type TLevelItem = record
     ItemType   :String;
     name       :String;
     image_file :String;
     image_iso_file :String;
     model_file :String;
     position   :TF3D_Vector3f;
     rotation   :TF3D_Vector3f;
     image_data :TImage;
     image_iso_data :TImage;
     drvl_A,drvl_B:TF3D_Vector3f;
     drvr_A,drvr_B:TF3D_Vector3f;
     event:String;
     end;
     
// *****************************************************************************
//  CLASS of LEVEL LIST ITEMS
// *****************************************************************************

type TLevelItemList = class
     private
     public
        item:array of TLevelItem;
        count:integer;
        constructor Create;
        destructor Destroy;
        procedure LoadFromFile(filename:String);

     
     end;


implementation

// *****************************************************************************
// constructor
// *****************************************************************************
constructor TLevelItemList.Create();
begin
    Inherited Create;
    self.count:=0;
    setLength(self.item,self.count);
    
end;

// *****************************************************************************
// destructor
// *****************************************************************************
destructor TLevelItemList.Destroy();
begin
    self.count:=0;
    setLength(self.item,self.count);
     Inherited Destroy;
end;

// *****************************************************************************
// load from file
// *****************************************************************************
procedure TLevelItemList.LoadFromFile(filename:String);
var i:integer;
    loader: TF3D_TextParser;
    BlockID: integer;
begin

    loader := TF3D_TextParser.Create();

    loader.Separator._BEGIN := '{';
    loader.Separator._END := '}';
    loader.Separator._SPACES := 10;
    loader.Separator._VALUE := ',';
    loader.Separator._NAME := ':';
    loader.Separator._IGNORE := ' ';



    loader.Load(filename);
    loader.Execute();

    self.count:=loader.BlocksCount;
    setLength(self.item,self.count);

    for BlockID := 0 to loader.BlocksCount - 1 do
    begin
        self.item[BlockID].ItemType    := loader.GetValueAsString(BlockID, 'type');
        self.item[BlockID].name        := loader.GetValueAsString(BlockID, 'name');
        self.item[BlockID].image_file  := loader.GetValueAsString(BlockID, 'image');
        self.item[BlockID].event       := loader.GetValueAsString(BlockID, 'event');
        self.item[BlockID].image_iso_file  := loader.GetValueAsString(BlockID, 'imageiso');
        self.item[BlockID].model_file  := loader.GetValueAsString(BlockID, 'model');
        self.item[BlockID].position    := loader.GetValueAsVector3f(BlockID, 'position');
        self.item[BlockID].rotation    := loader.GetValueAsVector3f(BlockID, 'rotation');
        
        self.item[BlockID].drvl_A      := loader.GetValueAsVector3f(BlockID, 'drvl_A');
        self.item[BlockID].drvl_B      := loader.GetValueAsVector3f(BlockID, 'drvl_B');
        self.item[BlockID].drvr_A      := loader.GetValueAsVector3f(BlockID, 'drvr_A');
        self.item[BlockID].drvr_B      := loader.GetValueAsVector3f(BlockID, 'drvr_B');


        self.item[BlockID].image_data := TImage.Create(nil);
        self.item[BlockID].image_data.Picture.LoadFromFile('editor/icons/'+self.item[BlockID].image_file);
        self.item[BlockID].image_iso_data :=TImage.Create(nil);
        self.item[BlockID].image_iso_data.Picture.LoadFromFile('editor/icons/'+self.item[BlockID].image_iso_file);

    end;
end;



end.

