unit AGFX_PARSER;

interface
uses classes,
    sysutils,
    dialogs,
    agfx_types;

type TSeparator = record
        _BEGIN: string;
        _END: string;
        _VALUE: string;
        _NAME: string;
        _IGNORE: string;
        _SPACES: Integer;

    end;

type TBlock = record
        _start: Integer;
        _end: Integer;
    end;

type Tcommands = record
        name: string;
        values_count: Integer;
        values: TStringList;
    end;

type TF3D_TextParser = class
    private

        Blocks: array of TBlock;
        CommandLines: array of Tcommands;
        CommandLinesCount: Integer;
        file_name: string;
        _line: string;
        _line_id: integer;
        _split: array[0..10] of string;
        function PrepareBlocks(): Integer;
        procedure PrepareCommands();

    public
        text: TStringList;
        Separator: TSeparator;
        BlocksCount: Integer;

        constructor Create();
        destructor Destroy();override;
        procedure SetText(txt: TStringList);
        procedure Load(name: string);
        procedure Execute();
        function ExistValue(bid: integer; vname: string): boolean;
        function GetValueAsString(BlockID: Integer; name: string): string;

        function GetValueAsInteger(BlockID: Integer; name: string): Integer;
        function GetValueAsFloat(BlockID: Integer; name: string): Single;
        function GetValueAsVector3f(BlockID: Integer; name: string): TF3D_Vector3f;
        function GetValueAsVector3i(BlockID: Integer; name: string): TF3D_Vector3i;
        function GetValueAsVector2f(BlockID: Integer; name: string): TF3D_Vector2f;
        function GetValueAsVector2i(BlockID: Integer; name: string): TF3D_Vector2i;
        function GetValueAsColor3f(BlockID: Integer; name: string): TF3D_COLOR3f;
        function GetValueAsColor4f(BlockID: Integer; name: string): TF3D_COLOR4f;
        function GetValueAsBoolean(BlockID: Integer; name: string): Boolean;

        procedure SetNextLine();
        procedure ReadLine();
        function isToken(substr: string): boolean;
        function GetParameter(id: integer): string;
        procedure Split();
        function GetVector3f(): TF3D_Vector3f;
        function GetVector2f(): TF3D_Vector2f;
        function GetColor4f(): TF3D_Color4f;
        function GetString(): string;
        function GetInteger(): integer;

    end;

implementation
// *****************************************************************************
// AGFX3D_Parser: constructor
// *****************************************************************************

constructor TF3D_TextParser.Create();
begin
    inherited create;
    text := TStringList.create();
    BlocksCount := 0;
    SetLength(Blocks, BlocksCount);
    CommandLinesCount := 0;
    SetLength(CommandLines, CommandLinesCount);
end;
// *****************************************************************************
// AGFX3D_Parser: destructor
// *****************************************************************************

destructor TF3D_TextParser.Destroy();
begin
    inherited destroy;
end;
// *****************************************************************************
// AGFX3D_Parser: set text for parse
// *****************************************************************************

procedure TF3D_TextParser.SetText(txt: TStringList);
begin
    text := txt;
end;
// *****************************************************************************
// AGFX3D_Parser: prepare command line
// *****************************************************************************

procedure TF3D_TextParser.PrepareCommands();
var l, s: Integer;
    name_pos: Integer;
    line: string;
    line_id: Integer;
    val_pos: Integer;
    value: string;
    //dbg:TstringList;
    correction: string;

begin
    //writeln('PARSE FILE: ' + file_name);
    CommandLinesCount := 0;
    SetLength(CommandLines, CommandLinesCount);
    //dbg:=TstringList.Create();

    for L := 0 to text.Count - 1 do
    begin
        inc(CommandLinesCount);
        line_id := CommandLinesCount - 1;
        SetLength(CommandLines, CommandLinesCount);
        CommandLines[line_id].values := TStringList.Create();


        line := text.Strings[l] + Separator._VALUE;

         // separate COMMAND NAME
        name_pos := pos(Separator._NAME, line);
        CommandLines[line_id].name := copy(line, 1, name_pos - 1);

        correction := CommandLines[line_id].name;

         //dbg.Add(CommandLines[line_id].name);
        CommandLines[line_id].values_count := 0;

         // remove _NAME separator
        line := copy(line, name_pos + 1, length(line));
        line := trimLeft(line);

         // separate COMMAND VALUES

        val_pos := pos(Separator._VALUE, line);

        if (length(line) > 1) and (val_pos >= 1) then
        begin
            value := '';
            for s := 1 to length(line) do
            begin

                if line[s] <> Separator._VALUE then
                begin
                    if line[s] <> #9 then
                    begin
                        value := value + line[s];
                    end;
                end;

                if line[s] = Separator._VALUE then
                begin
                    inc(CommandLines[line_id].values_count);
                    CommandLines[line_id].values.Add(value);
                    value := '';
                      //dbg.Add( CommandLines[line_id].values[CommandLines[line_id].values_count-1]);
                end;

            end;

        end;
    end;

    //dbg.SaveToFile('comannds.log');
    //dbg.Free();
end;

// *****************************************************************************
// TF3D_TextParser: load
// *****************************************************************************

procedure TF3D_TextParser.Load(name: string);
begin
    self.file_name := name;

    if not(fileExists(name)) then
    begin
         Dialogs.ShowMessage('MISSING FILE: '+name);
    end;

    text.loadfromfile(name);
    _line_id := -1;
end;

// *****************************************************************************
// AGFX3D_Parser: Prepare blocks
// *****************************************************************************

function TF3D_TextParser.PrepareBlocks(): Integer;
var l: Integer;
    BlockID: integer;
    //dbg:TStringList;
begin

    BlocksCount := 0;
    SetLength(Blocks, BlocksCount);
    //dbg:=TStringList.Create();
    for l := 0 to text.Count - 1 do
    begin
        if pos(Separator._BEGIN, text.Strings[l]) <> 0 then
        begin
            Inc(BlocksCount);
            SetLength(Blocks, BlocksCount);
            BlockID := BlocksCount - 1;
            Blocks[BlockID]._start := l + 1;
        end;

        if pos(Separator._END, text.Strings[l]) <> 0 then
        begin
            Blocks[BlockID]._end := l - 1;
              //dbg.Add('BLOCK ID: '+INtToStr(BlockID)+'='+IntToStr(Blocks[BlockID]._start)+' -> '+IntToStr(Blocks[BlockID]._end));
        end;
    end;

    //dbg.SaveToFile('block.log');
    //dbg.Free();

    result:=0;
end;

function TF3D_TextParser.ExistValue(bid: integer; vname: string): boolean;
var cid: integer;
    res: boolean;
begin
    res := false;
    for cid := Blocks[bid]._start to Blocks[bid]._end do
    begin
        if CommandLines[cid].name = vname then
        begin
            result := true;
            exit;
        end;
    end;


    result := res;
end;


// *****************************************************************************
// AGFX3D_Parser: EXECUTE parses
// *****************************************************************************

procedure TF3D_TextParser.Execute();
var l: integer;
    tmp: string;
    BCount: Integer;
begin

     // remove ignored character
    for l := 0 to text.Count - 1 do
    begin
        tmp := text.Strings[l];
        text.Strings[l] := StringReplace(tmp, Separator._IGNORE, '', [rfReplaceAll]);
    end;

     // remove TAB character
    for l := 0 to text.Count - 1 do
    begin
        tmp := text.Strings[l];
        text.Strings[l] := StringReplace(tmp, chr(9), '', [rfReplaceAll]);
    end;


     // prebare BLOCKS
    BCount := PrepareBlocks();

     // prepare Line Commands
    PrepareCommands();

end;

function TF3D_TextParser.GetValueAsString(BlockID: Integer; name: string): string;
var b: Integer;
begin
    for b := Blocks[BlockID]._start to Blocks[BlockID]._end do
    begin

        if CommandLines[b].name = name then
        begin
            result := CommandLines[b].values[0];
            exit;
        end;

    end;
    result := 'none';
end;

function TF3D_TextParser.GetValueAsInteger(BlockID: Integer; name: string): Integer;
var b: Integer;
begin
    for b := Blocks[BlockID]._start to Blocks[BlockID]._end do
    begin

        if CommandLines[b].name = name then
        begin
            result := StrToIntDef(CommandLines[b].values[0], 0);
            exit;
        end;

    end;
end;

function TF3D_TextParser.GetValueAsFloat(BlockID: Integer; name: string): Single;
var b: Integer;
begin
    for b := Blocks[BlockID]._start to Blocks[BlockID]._end do
    begin

        if CommandLines[b].name = name then
        begin
            result := StrToFloatDef(CommandLines[b].values[0], 0.0);
            exit;
        end;

    end;
end;

function TF3D_TextParser.GetValueAsVector3f(BlockID: Integer; name: string): TF3D_Vector3f;
var b: Integer;
begin
    for b := Blocks[BlockID]._start to Blocks[BlockID]._end do
    begin

        if CommandLines[b].name = name then
        begin
            result.x := StrToFloatDef(CommandLines[b].values[0], 0.0);
            result.y := StrToFloatDef(CommandLines[b].values[1], 0.0);
            result.z := StrToFloatDef(CommandLines[b].values[2], 0.0);
            exit;
        end;

    end;
end;

function TF3D_TextParser.GetValueAsVector3i(BlockID: Integer; name: string): TF3D_Vector3i;
var b: Integer;
begin
    for b := Blocks[BlockID]._start to Blocks[BlockID]._end do
    begin

        if CommandLines[b].name = name then
        begin
            result.x := StrToIntDef(CommandLines[b].values[0], 0);
            result.y := StrToIntDef(CommandLines[b].values[1], 0);
            result.z := StrToIntDef(CommandLines[b].values[2], 0);
            exit;
        end;

    end;
end;

function TF3D_TextParser.GetValueAsVector2f(BlockID: Integer; name: string): TF3D_Vector2f;
var b: Integer;
begin
    for b := Blocks[BlockID]._start to Blocks[BlockID]._end do
    begin

        if CommandLines[b].name = name then
        begin
            result.x := StrToFloatDef(CommandLines[b].values[0], 0.0);
            result.y := StrToFloatDef(CommandLines[b].values[1], 0.0);
            exit;
        end;

    end;
end;

function TF3D_TextParser.GetValueAsVector2i(BlockID: Integer; name: string): TF3D_Vector2i;
var b: Integer;
begin
    for b := Blocks[BlockID]._start to Blocks[BlockID]._end do
    begin

        if CommandLines[b].name = name then
        begin
            result.x := StrToIntDef(CommandLines[b].values[0], 0);
            result.y := StrToIntDef(CommandLines[b].values[1], 0);
            exit;
        end;

    end;
end;

function TF3D_TextParser.GetValueAsColor3f(BlockID: Integer; name: string): TF3D_COLOR3f;
var b: Integer;
begin
    for b := Blocks[BlockID]._start to Blocks[BlockID]._end do
    begin

        if CommandLines[b].name = name then
        begin
            result.R := StrToFloatDef(CommandLines[b].values[0], 0.0);
            result.G := StrToFloatDef(CommandLines[b].values[1], 0.0);
            result.B := StrToFloatDef(CommandLines[b].values[2], 0.0);
            exit;
        end;

    end;
end;

function TF3D_TextParser.GetValueAsColor4f(BlockID: Integer; name: string): TF3D_COLOR4f;
var b: Integer;
begin
    for b := Blocks[BlockID]._start to Blocks[BlockID]._end do
    begin

        if CommandLines[b].name = name then
        begin
            result.R := StrToFloatDef(CommandLines[b].values[0], 1.0);
            result.G := StrToFloatDef(CommandLines[b].values[1], 1.0);
            result.B := StrToFloatDef(CommandLines[b].values[2], 1.0);
            result.A := StrToFloatDef(CommandLines[b].values[3], 1.0);
            exit;
        end;

    end;
end;

function TF3D_TextParser.GetValueAsBoolean(BlockID: Integer; name: string): Boolean;
var b: Integer;
begin
    for b := Blocks[BlockID]._start to Blocks[BlockID]._end do
    begin

        if CommandLines[b].name = name then
        begin
            if (CommandLines[b].values[0] = 'true') then result := true;
            if (CommandLines[b].values[0] = 'false') then result := false;
            exit;
        end;

    end;
end;


procedure TF3D_TextParser.SetNextLine();
begin
    Inc(_line_id);
end;

procedure TF3D_TextParser.ReadLine();
begin
    self._line := self.text.Strings[_line_id];
    self.Split();
end;

function TF3D_TextParser.isToken(substr: string): boolean;
var res: boolean;
    find: integer;
begin
    res := false;
    find := pos(substr, _line);
    if find > 0 then res := true;

    result := res;
end;

procedure TF3D_TextParser.Split();
var sp, i: integer;
    find: integer;
    _tmp_line: string;
    loop: boolean;
begin
    sp := 0;

    for i := 0 to 10 do self._split[i] := '';

    _tmp_line := self._line;
    find := pos(':', _line);
    delete(_tmp_line, 1, find);

    loop := true;
    i := 1;

    while loop do
    begin
        if ((_tmp_line[i] <> ';') and (_tmp_line[i] <> '|')) then self._split[sp] := self._split[sp] + _tmp_line[i];
        if _tmp_line[i] = ';' then loop := false;
        if _tmp_line[i] = '|' then Inc(sp);
        inc(i);
    end;
    beep;
end;

function TF3D_TextParser.GetParameter(id: integer): string;
var left_range, right_range: integer;
    value: string;
begin
    if id = 1 then
    begin
        left_range := pos('|', _line);
        delete(_line, 1, left_range);
        right_range := pos('|', _line);

        value := copy(_line, 1, right_range - 1);
        result := value;
    end;
end;

function TF3D_TextParser.GetString(): string;
begin
    if self.isToken('<str>') then
    begin
        result := self._split[0];
    end;

end;

function TF3D_TextParser.GetInteger(): integer;
begin
    if self.isToken('<int>') then
    begin
        result := StrToIntDef(self._split[0], 0);
    end;

    result:=0;

end;

function TF3D_TextParser.GetVector2f(): TF3D_Vector2f;
begin
    if self.isToken('<v2f>') then
    begin
        result.X := StrToFloatDef(self._split[0], 0);
        result.Y := StrToFloatDef(self._split[1], 0);

    end
    else
        result := SetVector2f(0, 0);

end;

function TF3D_TextParser.GetVector3f(): TF3D_Vector3f;
begin
    if self.isToken('<v3f>') then
    begin
        result.X := StrToFloatDef(self._split[0], 0);
        result.Y := StrToFloatDef(self._split[1], 0);
        result.Z := StrToFloatDef(self._split[2], 0);
    end
    else
        result := SetVector3f(0, 0, 0);

end;

function TF3D_TextParser.GetColor4f(): TF3D_Color4f;
begin
    if self.isToken('<c4f>') then
    begin
        result.R := StrToFloatDef(self._split[0], 1);
        result.G := StrToFloatDef(self._split[1], 1);
        result.B := StrToFloatDef(self._split[2], 1);
        result.A := StrToFloatDef(self._split[3], 1);
    end
    else
        result := SetColor4f(1, 1, 1, 1);

end;

end.

