run:
	foreman start

compile:
	protoc -Isrc --python_out=gravitiq src/*.proto
	protoc -Isrc --proto_path=src --descriptor_set_out=build/grivitiq.protobin src/*.proto
	mono ProtoGen.exe -line_break=Unix build/grivitiq.protobin
