"""
"""

from cift.parser import Symbol, Seq, Or, Maybe, Many

ascii_all = set(map(chr, range(128)))
ascii_digits = set("0123456789")
ascii_upper = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

cif_file = Symbol("cif_file")
command = Symbol("command")
prim_command = Symbol("prim_command")
polygon_command = Symbol("polygon_command")
box_command = Symbol("box_command")
round_flash_command = Symbol("round_flash_command")
wire_command = Symbol("wire_command")
layer_command = Symbol("layer_command")
def_start_command = Symbol("def_start_command")
def_finish_command = Symbol("def_finish_command")
def_delete_command = Symbol("def_delete_command")
call_command = Symbol("call_command")
user_extension_command = Symbol("user_extension_command")
comment_command = Symbol("comment_command")
end_command = Symbol("end_command")

transformation = Symbol("transformation")

path = Symbol("path")
point = Symbol("point")

sinteger = Symbol("sinteger")
integer = Symbol("integer")
integer_d = Symbol("integer_d")
shortname = Symbol("shortname")
c = Symbol("c")
user_text = Symbol("user_text")
comment_text = Symbol("comment_text")

semi = Symbol("semi")
sep = Symbol("sep")
digit = Symbol("digit")
upper_char = Symbol("upper_char")
blank = Symbol("blank")
user_char = Symbol("user_char")
comment_char = Symbol("comment_char")

strict = {
    cif_file: Seq(
        Many(
            Seq(Many(blank), Maybe(command), semi)
            ),
        end_command,
        Many(blank)
        ),

    command: Or(
        prim_command,
        def_delete_command,
        Seq(
            def_start_command,
            semi,
            Many(
                Seq(
                    Many(blank),
                    Maybe(prim_command),
                    semi
                    ),
                ),
            def_finish_command,
            ),
        ),

    prim_command: Or(
        polygon_command,
        box_command,
        round_flash_command,
        wire_command,
        layer_command,
        call_command,
        user_extension_command,
        comment_command
        ),

    polygon_command: Seq('P', path),
    box_command: Seq(
        'B', integer, sep, integer, sep, point,
        Maybe(Seq(sep, point)),
        ),
    round_flash_command: Seq("R", integer, sep, point),
    wire_command: Seq("W", integer, sep, path),
    layer_command: Seq("L", Many(blank), shortname),
    def_start_command: Seq(
        "D", Many(blank), "S", integer,
        Maybe(Seq(sep, integer, sep, integer))
        ),
    def_finish_command: Seq("D", Many(blank), "F"),
    def_delete_command: Seq("D", Many(blank), "D", integer),
    call_command: Seq("C", integer, transformation),
    user_extension_command: Seq(digit, user_text),
    comment_command: Seq("(", comment_text, ")"),
    end_command: "E",

    transformation: Many(
        Seq(
            Many(blank),
            Or(
                Seq("T", point),
                Seq("M", Many(blank), "X"),
                Seq("M", Many(blank), "Y"),
                Seq("R", point),
                )
            )
        ),

    path: Seq(point, Many(Seq(sep, point))),
    point: Seq(sinteger, sep, sinteger),

    sinteger: Seq(Many(sep), Maybe("-"), integer_d),
    integer: Seq(Many(sep), integer_d),
    integer_d: Seq(digit, Many(digit)),

    shortname: Seq(c, Maybe(c), Maybe(c), Maybe(c)),
    c: Or(digit, upper_char),
    user_text: Many(user_char),
    comment_text: Or(
        Many(comment_char),
        Seq(comment_text, "(", comment_text, ")", comment_text)
        ),

    semi: Seq(Many(blank), ";", Many(blank)),
    sep: Or(upper_char, blank),
    digit: Or(*ascii_digits),
    upper_char: Or(*ascii_upper),
    blank: Or(*(ascii_all - ascii_digits - ascii_upper - set("-();"))),
    user_char: Or(*(ascii_all - set(";"))),
    comment_char: Or(*(ascii_all - set("()"))),
    }

lenient_char = Symbol("lenient_char")
lenient_layers = {
    **strict,
    shortname: Seq(lenient_char, Many(lenient_char)),
    lenient_char: Or(*set(
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "abcdefghijklmnopqrstuvwxyz"
        "0123456789"
        "-_"
        ))
    }

