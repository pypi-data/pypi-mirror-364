# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# See the License at http://www.apache.org/licenses/LICENSE-2.0
# Distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND.

"""
satellites
----------

This is a sample dataset build into the engine, this simplifies a few things:

- We can write test scripts using this data, knowing that it will always be available.
- We can write examples using this data, knowing the results will always match.

This data was obtained from:
https://github.com/devstronomy/nasa-data-scraper/blob/master/data/json/satellites.json

Licence @ 02-JAN-2022 when copied - MIT Licences attested, but data appears to be
from NASA, which is Public Domain.

To access this dataset you can either run a query against dataset :satellites: or you
can instantiate a SatelliteData() class and use it like a Relation.

This has a companion dataset, $planets, to help test joins.
"""

from orso.schema import FlatColumn
from orso.schema import RelationSchema
from orso.types import OrsoTypes

from opteryx.models import RelationStatistics

__all__ = ("read", "schema")

_decoded: bytes = None


def read(*args):
    import base64
    import io

    import pyarrow.parquet as pq

    global _decoded

    """The table is saved parquet table, base85 encoded."""
    if _decoded is None:
        _decoded = base64.b85decode(
            b"P(e~L6$BNK78RZZOcmk+6$BCh04TLD{a}a$EeHUH);=8&kgpv83;+xO3;+xO3_!^xmt1nmC6`=s$tBY%GXOOJIRLwI-KsS!)~i;lQk^O_D%7V=n=)OhG%3=fMvD?1Dl{n2pFVr?+^I7s&YL!C(wr$XCKXH&!2=B}kiY>23=qJ-e*5y>t2Zy+yLRi+ohvsk+_!GqvR$h-E!wkY%aR={HZ0h$UIA~ku|^talrcsaUv#lW7FSd;MHEjou|yI_6fr~)KlHFe4mZ>=LkusputEwalrTaFA9S!m1{VbXFv0xN%PzUxQp+r{ywb`lshm>ED4~4P$tIaxQpqHdJkrP_i5ybMAc6eR#~yjyQO6u{1c0zq0ssR66#x~20~M45EEVDc6$BLq6$Ts_2(bVF0000002l}X000000000M04NBt000000000O2mt^90000000000D77#BAi)U+00RI30OA4x2rmEu0s{mE1_uZU3JVMk4i69!5)%{^78e*98XFuP9v>hfA|oUvCMPH<Dl054E-x@KGBY$aHa9pqIy*c)K0iP~LPJDFMn_0VN=r;lPESx#Qd3k_R##YAT3cLQUSD8gVq;`wW@l(=YHMt5Zf|gLa&vTbc6WGrdV73*et&?0f`f#GhKGoWii?bmj*pO$l9QB`mY0~Bnwy-Ro}ZwhqNAjxrl+W>s;jK6uCK5F00000001W32pkmz88rj|1{oLvX=D`)7UBXHv>F!F2qwq`CI}oD2(bVF0000002l}X000000000M04NBt000000000O2mt^900000000>*6$BLo6#@Vi02Krk0ssI26$BM<6-Z1K4iy9v001bpFa01m-2ecf0{{d71po#B2LK2F2><{90000022=t70|6BP6)Y7#EEVDc6$BLq6$Ts_2nhfH0000002l}Z000000000M04N9v000000000O2m=5B0000000000D77#BAQrIz00RI30OA4x0|Q7TNqho&12zO41qucxwhSB<1Q|6100tQt2ykp+Ze?^yWEBh+;sO@50v4VECj1H}m<k*i2nhfH0000002l}Z000000000M04N9v000000000O2m=5B00000000>*6$BLo6#@Vi02Krk0ssI26$BNy9u<xdOcmk+6$BCh04TLD{a~C1?H>S&K}-uO@QQ4618G93ChMWpP|8}Or78Fxgq<KB!tMWCK%PE{6O&D3<tM-tAqAoUuK=z9FRcm1>}qQgH}Zd>Rkc(r<?+=p{5V>XWxL6~@MCCz-}VIN)PT@jE~`$8K4mVOBx>eL%>RbQbyH>@9N|*hFx<Kk;6}AXn9Uq2X~Qs$_^(jS%NL<KCEDV`E284J(SL?!s}|;^(@p*_a$QnO`QJ!w(Ipl6@8Ag6xs?2OC{yZsS>V4TD{gD@pTP$H1At7eI{arqmbhL1Gaj?$zaslul@2;t$}Y!w;T9VQ+00&p`;sn3{x29-mrIUNonoFkrD%&vZ8fo8R#Z}Mm#9@f-qz}({CB*Ji%D$=cpd&P;MJmHES65EH~Ig7NiC$}KoImmP{ny52!R0$0w52BKtO;(0;J+3JRqpzJkJ9O5W!YT^Hb+8iL!L6u_jfgM6*sQ&23tTpl#}f^4pEmhGEJPN}uI1r5UAYiwpDO5`sOhqJ`XIAK2!q#jVnT|BPITO7OqobUPt(7#>LEFg%g7@I=nSg8_;hg#;*a6e36AL12g+g=a!1s?{#AN%%S|R&2{T)<hZJPKecLxcl0el>dsz3|{j?KYjSm*l4BH`S9P7E<$Zs%4wz_@9{QC8~!_bGrA2rCH^m(y1Kp2jjG)4NsFo3Z1YMk^53zY3*542S^gtTSleJb^Q;)H=)Yqkdl?vL&^eLovX@fuU-4Koqmf9PD@OknkXxlzh-TMjCH@~gZU!XbC_t51WlC{IWc2?)TTCk9WnEG%jocRqw=+Uxx-9Uvg6aTax@;_$t+q=1XFQJEY%5Fhe<7tME^EEyTh<!2Gt+6A;7%|5!CBMW#=LBmM#z#zjan<n?bu}VbVVtxX0k5-70KSZ27BugGJ=iGQP)|O$CNVoNVX7aPcOH@X{!$WZ{#{<%@X#q*Ajq|s39Drq_j+lh)APKb6}z|MpYgV7}GR`4p>86l{BE~gDC@sB=*5wiQqU!B@W&vBDB_7nf_Dh&n3`YpTmR82$DgByY^>)Kr&J5Pd^#_2m?&x0p-b*pGD)FGyOCHmPi1Kb*&K%WJ+x$DdufoS8iXS!mjx1Wap!!b_B!e`m?CWdk@2J5>*$fw|JH{#x~VZE0rMe*B(@{(bP2YG8-sQY%u<Mv>FzFoavKAG$5SB2fORn3wH9FIYjUP$;%pZ9f`BIw8AivrAhmgk~ytF8gC%^G9?WmM?@I7wPC<neEBAnQ8xLRX_6nOlERk^_J#?BEL&$?He`&V$T9(Xy1U0a|Li$e!jHWFamq9IC|FGAyf|L`I`ajj<2I`b6#x~20~M45EEVDc6$BLq6$TtO04M}mZE12C2tj0WVRLk4VE_OCD77#BAi)U+00RI30OA4x2rmEu0s{mE1_uZU3JVMk4i69!5)%{^78e*98XFuP9v>hfA|oUvCMPH<Dl054E-x@KGBY$aHa9pqIy*c)K0iP~LPJDFMn_0VN=r;lPESx#Qd3k_R##YAT3cLQUSD8gVq;`wW@l(=YHMt5Zf|gLa&vTbc6WGrdV73*et&?0f`f#GhKGoWii?bmj*pO$l9QB`mY0~Bnwy-Ro}ZwhqNAjxrl+W>s;jK6uCK5F00000001VGA{-SA88rj|1{oLxZeeX@6$}>Q0v4<y7L*hwupTCW4jeWBC<Iw;X>u3{L1c1ab97~402wS51Qi4o0ss{N6$BLm0000L1Qp;66{rhL70dw@1QGxMD77#BU@!tz765c783a}i%_g%zVxz3zOiV{Vc59go$MYFKBis3Y>PNRgeLpo`dIhOKZxVyR>QBQ!i)`onNejF{M2l?a`>DY{&CJZq%*@<B83a}iEwZgYdlarm;d+#GKNXBh>I5`#KQC^h0lWo*Km4ij(oJGuKeA&Z5U=Y;Kbo1DnVFfnK!87xzDd)dXbwMng$4Hm9tc0TUp`qeT<t!hCi;Ao5$8VfXyb^r_|!g)?X{ry#^62$q9<iiL+d_N<PdRlD#<?n*|0tUzQGqJQw0P-$e6p9kk1@IrV2(Sb(%y#$Ok=}RYy`lwWfK;DL!LBC!mS25sAS-UkA<^QQFr(WA0i)J|JE|-L-^#(6iw`?G3&#nJU0P4d5-1p!lIbo(ztXSLaASi{O7N*|9M{fS+;UKu9J(ORzYc`PDo>kb@Ft+Wv(<u``9vYwUtQID{%Sd!RKxz&=7h57z%V%$FxW6f8f-y10!7@K!&`$L<0p1@=Cf@*$`iy$U~+_6A>=Ol9~!RX|`=KxSrUW@d(LKn!R=5kUHWYP@ulXg`w6e@MT5Z9fxX!_zBec|R9OQ2ZEkmp^nyl=cQ+h(FGV(%#?;qd%H=oT4MSyg!`8Ah2?1k(fW$#ceczx5z&V*Q0Pf3dcW2C3OOt2zx)^oDrqH!FNAfKdDWe-0x5{Khpcg*PdBIKfHOWLvDsUKVdReFe<52Lq9D;9P8pXDnCw^Kmb5Fw8(b8pNg43>`}NLh3mmT0MI`lh3iqc9@RhLdK9il;R=XrKRe$~jhAk6Ki+YQj^y%hKe|Z_0xO4xGe0vkGcz-jSwK}kdQv|f0K+7UIR>8Ef!ZUFiDhAI8P=xt9m1U{f@5bI%E~<rE&Kt<X6U%ty$QG0widU{Y$iiwv9^I$c3{ZJ42jFLRKA(agaMCO$t*jwzLu3J6#x~m0u{mnEEVDc6$BLq6$Ts_2yYUD!0J!KKo|%B00000004j%04NA=5`)0%Ps2bM2mk;800000fB*mhD77#BAeg}f00RI30OA4x2OWTbU_dAs4v2(e!Du)hkcebLsaP(UOh$9ra5x-|M$_qZIvq`i)6sM|8cwIv>2x|Bj;G`4bUK|*r_<?tKq1kHR5G1VDb<SAa=l=knCIg0z+^L8rB<=saJh=k<MDVrCLRqtUeEUf28Ban(Rf5A70M;E>3l+=QR$RgwO+AV?Uvj1e!*e!m|XS%04B0B92E)~H3R?#85ja*Z50d_;sO@35EhINCh#sMrXw5}2yYUD!0J!KKo|%B00000004j%04NA=5`)0%Ps2bM2mk;800000fB+dR6$BLo6#@Vi02Krk0ssI26$BOV3l;bTOclNX6$BCh04TLD{b2Y3l?ec(3;+NC001VNKr<#l&CD1;W@ct)W_Fxon2w}CnwgoInbe}(R6qa#0000$Re(hRJ~J{mEF`8#W*~qyGZ6p~nFR#?KLN}H`9CuYKmY*vKk(o`#%P0YsDO=u;)g&fT#v$a9i-r3{Dz=fU{(xGnK8^LW+gK&j73>QEX?#jW)AGrKO!bT9zYljATSg(2p57yf~Sbfhk0!oG&MVbL_tbX078I9Kvcj|0691+C?%CZWq?2cRzO&406#W0+=4&=00000fIdK3s1R6NHVyzIve^L;5Q9ET)B2l>Y4+iNXMXBl8f=&1w$3&$q&@k6zMFO7sW#kJLhQ7_-Z~aH9C-cRnAxzA>-;l%S%{~{oX{@hL@x8hxqVLC%Z|Y|^m{wMoK_r~-6hyg$Q1w;)B+Xe0xT8c0u=-m1{DSz7zk!&W@cuNq(B%5Gcz+YGc(ga762#+W@ct)W{#vl7zi^nGcz+Y(?0+J04TLD{UEAQ1pos80080w0S7ODfM7r<7!HVpV!>!Q9*~G+LaA6Tm`p}<*>E_VPN(DXcs!nthvVsZI3141<MDVr9?r+}@pwEQkH_QjfI^}Xsbo5#QmPfJ<$A$l8jEa3tJ!Y2oNlM%QF=a|?)UrYES%r(_xt^Rzu)g?`Eh=h9|sr|4v9tM5t&pjnN272361h>x5q;|wNa~9<nxNnYJFR-!q#ng9S;Bi00000Ch$BQ6$%+O1ONsZ7zT1-WNCGC6$}>Q0v6^E7JvyRia93mGaMKQW@ct)W{#vl7zi^nGcz+Y(?1pfC<ta|W@cuNq(B%5Gcz+YGc(ga02wS51Qi4o0ss{N6$BLm0000L1Qmb<6~qKg6;Krf5&!@wwJ-f(Kmf%E05lJcmu?b+zzRUY%ArNJ^Zh^Yr^ZV+iT6L#O=1vOISfFw$acP;8VEq&PmPyu68}H)(oJFzSp7d<x=9QIE9*ba%*@Qp%mhFH2ta1?Kkj@#HD0>;KZ!wL<<KJUKLl0|EwY{W^FQe(F$k<2{y&_=Ah2?1;Xj8K+0OS<@jqyh?R-Bq`adaLkHYmR<Ue~9u1Dc|<Uau5KXE+@*Q0RVKe!%+>ruGgKV08G;d&IVN8#E(!}Ta!kHXbIW&%J)w)6eec=`7~WINwajhFgAi)`onsqy$f27#4Bi){1sKlncYKsovVK$@AEnVFgC_CE~(W5_o&FTrYKD~w^_mX^oPq=aj?Qn4b2yW5!<G?xe<3KakqrU4bW0W1~b0u=-m1{DSz7zoo%Vh~t43_utN!}Ta!kHXbI76K>;(@kO!SUC(p7zo4lC|r-i)jt3L04TLD{UB4B0ssX7007_u0RjL913(}QL}45d2m?uyAP9mWTnGos!ZgkUMbbo7Rb^dRR#lZ&RZ1HLT<3jY7=~dOhG7_r5F!U*7>;5XhG7_rq9}?XS(+yR04CB!92E)~H3R?#85jp-Wo~n6ba@pF7UBXH#s?Oh2PT?BCbm8t7zoo%Vh~t43_utN!}Ta!kHXbI76K>;(@kO!SUC(p7zo4lC|r-i)jt3kEENP51Qh}R6#x|k6#@VN02KrkunZOE1xyvj0Tl!i001bpFa2N`0!<45q75}PaBJEyy1W$E2-=V0H^?B?Jx4xx=)@QG-L0OdKhRZyUN?GW?<8p(5G^7xgD6<4jl&gWpWrBQODNPvU@*MQfILcR#~-roPTKoL1+)1?k2Ty$%QW66?|6@Q(z5NoRM1?gki|<1E!*zEUlIr$APeVZ-r9iFxhb3$Q#bRJD%_ZrF6gdGPyiqLQ4gx=cB~R(nXQyE#|7sRM(f+NJ4|9H8A_9g_I$*>RW0}e7-Nhl9sslXL=}e*ph6XzOZD$Pwd)&bt+n=aDhQB;^D+TfsIh2Q%c)atPy$gZiyIISWAOt+!Q0rl+e=y_cTdant7KEOsog{KxQL6plyb-V??~H_Cs@F>CUoB5lQ1=6qi6WYn6ymL<A8C#0I#qy9HJd0ZHO%z)3(QX$dzSVM_4owyJutVnY4NFoxk392upC?(v+=_kMq*UrmchPXLb6JkN`aB^rZm3(mFJ_R22Xf&;k|W0xT8c0u=-m1{DSz7zh9W00000J3tr+dlarm;d&{+77Qo|000000028c7zle5u1Dc|DZl^#04TLD{UE481po*D006K70RzCI0RaasfPi2?C>Rcigkr&9G#rTsBqEtmDwfLyQ^{yHoK6Sh@q9iYOsFElj7T36sAM{UOrO)Jgc5~JqY@}J5~)_Kmg@zJ$zU^D?P0sgaFkq!gyQISB@+*&>-l~<U{Kf-p@c&su!kBFhee^VXFMX4N9B^)bUvX`>6ChkfI_}%uxKp_uUJP`tJ!j?!)~`L^nOj?uowUU001V0Q5+Qt88rj|1{oL$ZDD6_X>@gDWfcq-;sO?;5EkkQCZbIynnxTM2mk;80000xKo|&n6s||%dMUsb3@8Wy0000006Rb!2zwN+N8x%YzyKL66$BLo6#@Vi02Krk0ssI26$BNa1{JCWOci7m1QGxMD77#BV2}V^3IJpgxE_V;QMkT8lNbb64lS}joWvloa%izXDO``j^(f>&aXkvxqj2Rvh3iqc9);UK!}Ta!kHW=23fH4>Jqou!dlarm;d-P$s`1iIVi2f5nwgoInVGpi2&^1hWIL}vVh~t4w8-v10QNsbi)`onsq;Tp4lS~s@9#g6?R-BqUhc_1Gcz+YGc(iUKO@`uermk5KjuGN=lbyV+2F1}_9$GB!u8lc;d&IVN8!ppNYTyIKkQMs9);_%KcsLy3fH5su|FFx-6RHqwX;7v-%pK~Zn8i0{nU8rCb2&`w8(b8pSrp~HD0<&3<Bpr*TX-uo$sf{OSeDMO+Wg6YP@ulxIY3bhZfn+*FR=vW@ct));|*f6)Rt5FKTLeY%I$&%V24;Y?U`l3rjiKakrpjt9P;mcV`^dyud3n&`LgSl_PCI6cqp!xB(T)0W1~b0u=-m1{DSz7znr?h3iqc`ac*5dlarm;d-P$77Qo|xE_V;QMmd)7zle5u1Dc|q(1-v04TLD{UBW70ssgA006K70RzCI0RaXBKp+f6VH^+$1BtRA2!bG72nkH%JWwP}RApUQrcK+%aU92S9LI4ShafHp1)cYSp(u`IX_6<JA`l1%qAITJ*&c5DA_#&Y3LM9A3;-tNS{xM$88rj|1{oLzVQgY$WN#G=7UBXH_y`u12qv0XCeTtG7znr?h3iqc`ac*5dlarm;d-P$77Qo|xE_V;QMmd)7zle5u1Dc|q(1-|EENP51Qh}R6#x|k6#@VN02KlmoHYO#26JO*Wo=;<5C9bfB?1@%X=DHu1SJ9(2ykp+Ze?^yWB?TmB?1@(ZeeX@B>+qu0000L3MB#<0%vUi6$&K+7zT1-WNCGC02K-)0vHEmWo~n6ba?<33MB#<32k9#ZfSINWMu#q3MB#<24QSsWn^yv7UBXK92txz+z1>M1Q|6100tQt0%>Fw3>M-77PJ}`)CeZX1SSX^7znWd00000000;W0RR9100000762#+u>b%7000007zhCX000000000PEENP51Qh}R6#x|k6#@VN04BB!92Eo^H3R?#85js~Y+-I?bV+0t3>M-77PJBuo&qNP3MQBe92f`*000000000O2m=5B0000002Tl!2nhfH0000002l}Z000000000087vh96$BLm02Kfg1Qh}R001VGA{-SA88rj|1{oLxZeeX@6$}>Q0v4<y7L*hwupTCW4jeWBC<Iw;X>u3{L1c1ab97~402wS51Qi4o0ss{N6$BLm0000cvN9YM3K=y700tQt0%vU%3>M-77P1f)j1MO8E+(cU92f|15`)0%Ps2bM2mk;800000fEEBK2yYUD!0J!KKo|%B00000004jh87vh96$BLm02Kfg1Qh}R001WNJRB7Y88rj|1{oLza$#g?b#oOA7UBXH<_{Kt2_}j;Ch#*H7zk!&W@cuNq(B%5Gcz+YGc(ga762#+W@ct)W{#vl7zi^nGcz+Y(?0+iEENP51Qh}R6#x|k6#@VN04CB!92E)~H3R?#85jp-Wo~n6ba@pF7UBXH#s?Oh2PT?BCbm8t7zoo%Vh~t43_utN!}Ta!kHXbI76K>;(@kO!SUC(p7zo4lC|r-i)jt3kEENP51Qh}R6#x|k6#@VN049V{92E)~H3R?#85jv|VP|e>baiB96$}>Q0v4hW7U~HmqD>~6M;sUk000000028c7zle5u1Dc|DZmyCC<p)m00000J3tr+dlarm;d&{+02wS51Qi4o0ss{N6$BLm0000c<XRjR3K=y700tQt24QSsWn^y^3>M-77WfDjln5r8SSHX?92f|=9);^sxcWaB2zwN+N8x&;KNbuq2)G`F>ruG+KNtvm6s||%dZa%987vh96$BLm02Kfg1Qh}R000(@fB_cb0w&xD7OYSd000>r7z{yDQcqVpb7N>_ZDAOI1urizFE2S~LP0@6Q9(gLK|w)5OF=<*K|*IiMnOSmK|^OjK|w)5LP9}7O+i6HK|?`7NkKtDK|(=6NkKtDK|(=6K|w)hK|w)6FhNm4K}<nKK|xS=K|w)8NkKtDL2W@nK|x1nK|w)5FhM~<K|(=6K|xG<D=#lNK|w)9L`6YCK|w-iK|w)5ML|J9K|w)5K|w)TK|w)6Xktf7Y+6S+K|w_~FE1}RK|w)DK{ik~FE4jNK|xVXQ9(gLK}bPCK|w)LK|w)5K|w)5K|@hNK|x0`Xj(EgaAZhUYg$o3K|x42FE1}RK|w)DK}S$8FE4jNK|xVXQ9(gLK}SJBK|w)LK|w)5K|w)5K|*&yK|x1SY+`OsaAZhpL2-63FE4jNK|yCiMK3QeFF`>;LP2;zK|w)5SwTTTK|(=6K|w)5K|w)5M?pbBL1S%3YhhScdO<-%S1&IwFF`>;LqSMHFE1}RK|w)9L`6YCK|w-yK|w)5ML|J9K|w)5K|w)DK|w)6ZemeEK|w)5M?pbnK|*IiM?pbBK|w)5LqSVKFE1}RK|w)9MnyqEK|w-yK|w)5ML|J9K|w)5K|w)LK|w)6by-(2Y(YUmK|w)LK|(=6ML|J9L3&UxFE4jNK|xVTQ9(gLK}bPCK|w)LK|w)5K|w)5K|?`7K|x4Db6Hn4Y-B}jYe7LlK|xJaFE1}RK|w)5LQz3MK|w-6K}JDANkKtbK|*&yO+i6HK}A79Q9(gLK|w)5LP2OjK|w)5V?jYdK|(=6K|w)5K|w)5LqS17L19->K|w)hK}118NkKtlK|?`7K|w)5K|w)AK|w)5K>!#ZaA9(Bb!BudV{mXSVRCYBcOZ6Ua&u{KZXh)-FfK3|j2r*}8~^|u000~S02}}S8~^|u000~S003PE002-yQZW"
        )

    return pq.read_table(io.BytesIO(_decoded))


def schema():
    # fmt:off
    return RelationSchema(
            name="$satellites",
            columns=[
                FlatColumn(name="id", type=OrsoTypes.INTEGER),
                FlatColumn(name="planetId", type=OrsoTypes.INTEGER, aliases=["planet_id"]),
                FlatColumn(name="name", type=OrsoTypes.VARCHAR),
                FlatColumn(name="gm", type=OrsoTypes.DOUBLE),
                FlatColumn(name="radius", type=OrsoTypes.DOUBLE),
                FlatColumn(name="density", type=OrsoTypes.DOUBLE),
                FlatColumn(name="magnitude", type=OrsoTypes.DOUBLE),
                FlatColumn(name="albedo", type=OrsoTypes.DOUBLE),
            ],
        )


def statistics() -> RelationStatistics:
    stats = RelationStatistics()

    # fmt:off
    stats.record_count = 177
    stats.lower_bounds = {'id': 1, 'planetId': 3, 'name': 'Adrastea', 'gm': -0.0, 'radius': 0.3, 'density': 0.34, 'magnitude': -12.74, 'albedo': 0.04}
    stats.upper_bounds = {'id': 177, 'planetId': 9, 'name': 'Ymir', 'gm': 9887.834, 'radius': 2631.2, 'density': 3.528, 'magnitude': 27.0, 'albedo': 1.67}
    stats.null_count = {'id': 0, 'planetId': 0, 'name': 0, 'gm': 0, 'radius': 0, 'density': 0, 'magnitude': 0, 'albedo': 0}
    # fmt:on
    return stats
