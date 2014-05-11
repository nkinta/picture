# -*- coding: utf-8 -*-

UNKOWN_TYPE, BYTE, ASCII, SHORT, LONG, RATIONAL, SBYTE, UNDEFINED, SSHORT, SLONG, SRATIONAL, FLOAT, DFLOAT = range(0x00, 0x0D)
data_type_dict = {
            UNKOWN_TYPE: "UNKOWN_TYPE",
            BYTE: "BYTE",
            ASCII: "ASCII",
            SHORT: "SHORT",
            LONG: "LONG",
            RATIONAL: "RATIONAL",
            SBYTE: "SBYTE",
            UNDEFINED: "UNDEFINED",
            SSHORT: "SSHORT",
            SLONG: "SLONG",
            SRATIONAL: "SRATIONAL",
            FLOAT: "FLOAT",
            DFLOAT: "DFLOAT",
             }

data_struct_dict = {
            UNKOWN_TYPE: "B",
            BYTE: "B",
            ASCII: "s",
            SHORT: "H",
            LONG: "L",
            RATIONAL: "LL",
            SBYTE: "b",
            UNDEFINED: "B",
            SSHORT: "h",
            SLONG: "l",
            SRATIONAL: "ll",
            FLOAT: "f",
            DFLOAT: "d",
             }

data_type_size_dict = {
            UNKOWN_TYPE: 0x01,
            BYTE: 0x01,
            ASCII: 0x01,
            SHORT: 0x02,
            LONG: 0x04,
            RATIONAL: 0x08,
            SBYTE: 0x01,
            UNDEFINED: 0x01,
            SSHORT: 0x02,
            SLONG: 0x04,
            SRATIONAL: 0x08,
            FLOAT: 0x04,
            DFLOAT: 0x08,
             }

ANY = -1

tag_list = [
    ("ImageWidth", u"画像の幅", 0x0100, (SHORT, LONG), 1, -1,),
    ("ImageLength", u"画像の高さ", 0x0101, (SHORT, LONG), 1, -1,),
    ("BitsPerSample", u"画像のビットの深さ", 0x0102, SHORT, 3, -1,),
    ("Compression", u"圧縮の種類", 0x0103, SHORT, 1, -1,),
    ("PhotometricInterpretation", u"画素構成", 0x0106, SHORT, 1, -1,),
    ("ImageDescription", u"画像タイトル", 0x010E, ASCII, ANY, 1,),
    ("Make", u"画像入力機器のメーカー名", 0x010F, ASCII, ANY, 1,),
    ("Model", u"画像入力機器のモデル名", 0x0110, ASCII, ANY, 1,),
    ("StripOffsets", u"画像データのロケーション", 0x0111, (SHORT, LONG), None, -1,),
    ("Orientation", u"画像方向", 0x0112, SHORT, 1, 1,),
    ("SamplesPerPixel", u"コンポーネント数", 0x0115, SHORT, 1, -1,),
    ("RowsPerStrip", u"1ストリップあたりの行の数", 0x0116, (SHORT, LONG), 1, -1,),
    ("StripByteCounts", u"ストリップの総バイト数", 0x0117, (SHORT, LONG), None, -1,),
    ("XResolution", u"画像の幅の解像度", 0x011A, RATIONAL, 1, 2,),
    ("YResolution", u"画像の高さの解像度", 0x011B, RATIONAL, 1, 2,),
    ("PlanarConfiguration", u"画像データの並び", 0x011C, SHORT, 1, -1,),
    ("ResolutionUnit", u"画像の幅と高さの解像度の単位", 0x0128, SHORT, 1, 2,),
    ("TransferFunction", u"再生階調カーブ特性", 0x012D, SHORT, 3*256, 0,),
    ("Software", u"ソフトウェア", 0x0131, ASCII, ANY, 0,),
    ("DateTime", u"ファイル変更日時", 0x0132, ASCII, 20, 1,),
    ("Artist", u"アーティスト", 0x013B, ASCII, ANY, 0,),
    ("WhitePoint", u"参照白色点の色度座標値", 0x013E, RATIONAL, 2, 0,),
    ("PrimaryChromaticities", u"原色の色度座標値", 0x013F, RATIONAL, 6, 0,),
    ("JPEGInterchangeFormat", u"JPEGのSOIへのオフセット", 0x0201, LONG, 1, -1,),
    ("JPEGInterchangeFormatLength", u"JPEGデータのバイト数", 0x0202, LONG, 1, -1,),
    ("YCbCrCoefficients", u"色変換マトリクス係数", 0x0211, RATIONAL, 3, 0,),
    ("YCbCrSubSampling", u"YCCの画素構成(Cの間引き率)", 0x0212, SHORT, 2, -1,),
    ("YCbCrPositioning", u"YCCの画素構成(YとCの位置)", 0x0213, SHORT, 1, 2,),
    ("ReferenceBlackWhite", u"参照黒色点値と参照白色点値", 0x0214, RATIONAL, 6, 0,),
    ("Copyright", u"撮影著作権者/編集著作権者", 0x8298, ASCII, ANY, 0,),
    ("Exif_IFD_Pointer", u"Exifタグ", 0x8769, LONG, 1, 2,),
    ("GPSInfo_IFD_Pointer", u"GPSタグ", 0x8825, LONG, 1, 0,),

    ("ExposureTime", u"露出時間", 0x829A, RATIONAL, 1, 1,),
    ("FNumber", u"Fナンバー", 0x829D, RATIONAL, 1, 0,),
    ("ExposureProgram", u"露出プログラム", 0x8822, SHORT, 1, 0,),
    ("SpectralSensitivity", u"スペクトル感度", 0x8824, ASCII, ANY, 0,),
    ("PhotographicSensitivity", u"撮影感度", 0x8827, SHORT, ANY, 0,),
    ("OECF", u"光電変換関数", 0x8828, UNDEFINED, ANY, 0,),
    ("SensitivityType", u"感度種別", 0x8830, SHORT, 1, 0,),
    ("StandardOutputSensitivity", u"標準出力感度", 0x8831, LONG, 1, 0,),
    ("RecommendedExposureIndex", u"推奨露光指数", 0x8832, LONG, 1, 0,),
    ("ISOSpeed", u"ISOスピード", 0x8833, LONG, 1, 0,),
    ("ISOSpeedLatitudeyyy", u"ISOスピードラチチュードyyy", 0x8834, LONG, 1, 0,),
    ("ISOSpeedLatitudezzz", u"ISOスピードラチチュードzzz", 0x8835, LONG, 1, 0,),
    ("ExifVersion", u"Exifバージョン", 0x9000, UNDEFINED, 4, 2,),
    ("DateTimeOriginal", u"原画像データの生成日時", 0x9003, ASCII, 20, 0,),
    ("DateTimeDigitized", u"デジタルデータの作成日時", 0x9004, ASCII, 20, 0,),
    ("ComponentsConfiguration", u"各コンポーネントの意味", 0x9101, UNDEFINED, 4, 2,),
    ("CompressedBitsPerPixel", u"画像圧縮モード", 0x9102, RATIONAL, 1, 0,),
    ("ShutterSpeedValue", u"シャッタースピード", 0x9201, SRATIONAL, 1, 0,),
    ("ApertureValue", u"絞り値", 0x9202, RATIONAL, 1, 0,),
    ("BrightnessValue", u"輝度値", 0x9203, SRATIONAL, 1, 0,),
    ("ExposureBiasValue", u"露光補正値", 0x9204, SRATIONAL, 1, 0,),
    ("MaxApertureValue", u"レンズ最小Ｆ値", 0x9205, RATIONAL, 1, 0,),
    ("SubjectDistance", u"被写体距離", 0x9206, RATIONAL, 1, 0,),
    ("MeteringMode", u"測光方式", 0x9207, SHORT, 1, 0,),
    ("LightSource", u"光源", 0x9208, SHORT, 1, 0,),
    ("Flash", u"フラッシュ", 0x9209, SHORT, 1, 1,),
    ("FocalLength", u"レンズ焦点距離", 0x920A, RATIONAL, 1, 0,),
    ("SubjectArea", u"被写体領域", 0x9214, SHORT, 2/3/4, 0,),
    ("MakerNote", u"メーカノート", 0x927C, UNDEFINED, ANY, 0,),
    ("UserComment", u"ユーザコメント", 0x9286, UNDEFINED, ANY, 0,),
    ("SubSecTime", u"DateTimeのサブセック", 0x9290, ASCII, ANY, 0,),
    ("SubSecTimeOriginal", u"DateTimeOriginalのサブセック", 0x9291, ASCII, ANY, 0,),
    ("SubSecTimeDigitized", u"DateTimeDigitizedのサブセック", 0x9292, ASCII, ANY, 0,),
    ("FlashpixVersion", u"対応フラッシュピックスバージョン", 0xA000, UNDEFINED, 4, 2,),
    ("ColorSpace", u"色空間情報", 0xA001, SHORT, 1, 2,),
    ("PixelXDimension", u"実効画像幅", 0xA002, (SHORT, LONG), 1, 2,),
    ("PixelYDimension", u"実効画像高さ", 0xA003, (SHORT, LONG), 1, 2,),
    ("RelatedSoundFile", u"関連音声ファイル", 0xA004, ASCII, 13, 0,),
    ("Interoperability_IFD_Pointer", u"互換性IFDへのポインタ", 0xA005, LONG, 1, 0,),
    ("FlashEnergy", u"フラッシュ強度", 0xA20B, RATIONAL, 1, 0,),
    ("SpatialFrequencyResponse", u"空間周波数応答", 0xA20C, UNDEFINED, ANY, 0,),
    ("FocalPlaneXResolution", u"焦点面の幅の解像度", 0xA20E, RATIONAL, 1, 0,),
    ("FocalPlaneYResolution", u"焦点面の高さの解像度", 0xA20F, RATIONAL, 1, 0,),
    ("FocalPlaneResolutionUnit", u"焦点面解像度単位", 0xA210, SHORT, 1, 0,),
    ("SubjectLocation", u"被写体位置", 0xA214, SHORT, 2, 0,),
    ("ExposureIndex", u"露出インデックス", 0xA215, RATIONAL, 1, 0,),
    ("SensingMethod", u"センサ方式", 0xA217, SHORT, 1, 0,),
    ("FileSource", u"ファイルソース", 0xA300, UNDEFINED, 1, 0,),
    ("SceneType", u"シーンタイプ", 0xA301, UNDEFINED, 1, 0,),
    ("CFAPattern", u"CFAパターン", 0xA302, UNDEFINED, ANY, 0,),
    ("CustomRendered", u"個別画像処理", 0xA401, SHORT, 1, 0,),
    ("ExposureMode", u"露出モード", 0xA402, SHORT, 1, 1,),
    ("WhiteBalance", u"ホワイトバランス", 0xA403, SHORT, 1, 1,),
    ("DigitalZoomRatio", u"デジタルズーム倍率", 0xA404, RATIONAL, 1, 0,),
    ("FocalLengthIn35mmFilm", u"35mm換算レンズ焦点距離", 0xA405, SHORT, 1, 0,),
    ("SceneCaptureType", u"撮影シーンタイプ", 0xA406, SHORT, 1, 1,),
    ("GainControl", u"ゲイン制御", 0xA407, SHORT, 1, 0,),
    ("Contrast", u"撮影コントラスト", 0xA408, SHORT, 1, 0,),
    ("Saturation", u"撮影彩度", 0xA409, SHORT, 1, 0,),
    ("Sharpness", u"撮影シャープネス", 0xA40A, SHORT, 1, 0,),
    ("DeviceSettingDescription", u"撮影条件記述情報", 0xA40B, UNDEFINED, ANY, 0,),
    ("SubjectDistanceRange", u"被写体距離レンジ", 0xA40C, SHORT, 1, 0,),
    ("ImageUniqueID", u"画像ユニークID", 0xA420, ASCII, 33, 0,),
    ("CameraOwnerName", u"カメラ所有者名", 0xA430, ASCII, ANY, 0,),
    ("BodySerialNumber", u"カメラシリアル番号", 0xA431, ASCII, ANY, 0,),
    ("LensSpecification", u"レンズの仕様情報", 0xA432, RATIONAL, 4, 0,),
    ("LensMake", u"レンズのメーカ名", 0xA433, ASCII, ANY, 0,),
    ("LensModel", u"レンズのモデル名", 0xA434, ASCII, ANY, 0,),
    ("LensSerialNumber", u"レンズシリアル番号", 0xA435, ASCII, ANY, 0,),
    ("Gamma", u"再生ガンマ", 0xA500, RATIONAL, 1, 0,),
    
    ("ArwJpegDataStart", u"ARW専用jpegの先頭", 0xA500, LONG, 1, 0,),
    ]

tag_id_to_name_dict = {}
for temp_tuple in tag_list:
    tag_id_to_name_dict[temp_tuple[2]] = (temp_tuple[0], temp_tuple[1], temp_tuple[3], temp_tuple[4], temp_tuple[5])

tag_name_to_id_dict = {}
for temp_tuple in tag_list:
    tag_name_to_id_dict[temp_tuple[0]] = (temp_tuple[2], temp_tuple[1], temp_tuple[3], temp_tuple[4], temp_tuple[5])


def main():
    result_dict = {}
    for temp_tuple in tag_list:
        result_dict[temp_tuple[2]] = (temp_tuple[0], temp_tuple[1], temp_tuple[3], temp_tuple[4], temp_tuple[5])
    import pprint
    pprint.pprint(result_dict)
    
if __name__ == "__main__":
    main()
