

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<html>
<head>
    <title>-: SMC - Online Application Home :-</title>
    <meta content="Microsoft Visual Studio .NET 7.1" name="GENERATOR" />
    <meta content="Visual Basic .NET 7.1" name="CODE_LANGUAGE" />
    <meta content="JavaScript" name="vs_defaultClientScript" />
    <meta content="http://schemas.microsoft.com/intellisense/ie5" name="vs_targetSchema" />
    <meta http-equiv="Pragma" content="no-cache" />
    <meta http-equiv="Expires" content="0" />
    <meta http-equiv="Cache-Control" content="no-cache" />
    <link href="GeRegStyles.css" rel="stylesheet" type="text/css">
    <script type="text/javascript" language="javascript">
        (function () {
            function trimTrailingSlashes(value) {
                return value ? value.replace(/\/+$/, "") : "";
            }

            function uniqueOrigins(items) {
                var results = [];
                var seen = {};
                var i;
                var item;

                for (i = 0; i < items.length; i++) {
                    item = trimTrailingSlashes(items[i]);

                    if (!item || seen[item]) {
                        continue;
                    }

                    seen[item] = true;
                    results.push(item);
                }

                return results;
            }

            var configuredOrigin = trimTrailingSlashes(window.SMC_CHAT_SERVER_ORIGIN || "");
            var currentOrigin = "";

            if (window.location.protocol === "http:" || window.location.protocol === "https:") {
                currentOrigin = trimTrailingSlashes(window.location.origin);
            }

            window.SMC_CHAT_SERVER_ORIGINS = uniqueOrigins([
                configuredOrigin,
                "http://127.0.0.1:8086",
                "http://localhost:8086",
                currentOrigin
            ]);

            window.getSmcChatUrl = function (path, index) {
                var origins = window.SMC_CHAT_SERVER_ORIGINS || [];
                var targetPath = path || "";
                var origin = origins[index || 0] || "";

                if (targetPath && targetPath.charAt(0) !== "/") {
                    targetPath = "/" + targetPath;
                }

                return origin + targetPath;
            };

            window.loadSmcChatStylesheet = function (index) {
                var head = document.getElementsByTagName("head")[0];
                var link = document.createElement("link");
                var nextIndex = (typeof index === "number" ? index : 0) + 1;

                if (!head || !window.SMC_CHAT_SERVER_ORIGINS[index || 0]) {
                    return;
                }

                link.rel = "stylesheet";
                link.type = "text/css";
                link.href = window.getSmcChatUrl("/static/chatbot-widget.css?v=3", index || 0);
                link.onerror = function () {
                    if (nextIndex < window.SMC_CHAT_SERVER_ORIGINS.length) {
                        window.loadSmcChatStylesheet(nextIndex);
                    }
                };

                head.appendChild(link);
            };

            window.setSmcChatAsset = function (element, attributeName, assetPath, index) {
                var nextIndex = (typeof index === "number" ? index : 0);

                if (!element || !window.SMC_CHAT_SERVER_ORIGINS[nextIndex]) {
                    return;
                }

                element.setAttribute(attributeName, window.getSmcChatUrl(assetPath, nextIndex));
                element.onerror = function () {
                    window.setSmcChatAsset(element, attributeName, assetPath, nextIndex + 1);
                };
            };

            window.loadSmcChatStylesheet(0);
        })();
    </script>
    <%  %>
    <script type="text/javascript" language="javascript">        function DisableBackButton() {            window.history.forward()        }        DisableBackButton();        window.onload = DisableBackButton;        window.onpageshow = function (evt) { if (evt.persisted) DisableBackButton() }        window.onunload = function () { void (0) }        function ValidateForm() {            var ChkBxFatVal = document.all("chkagree");            var ChkBxFatVal1 = document.all("Chkagree1");            if (ChkBxFatVal.checked == false) {                alert('Check  "Accept the Terms & Conditions" to Proceed')                return false;            }            if (ChkBxFatVal1.checked == false) {                alert('Check  "Accept the Terms & Conditions" to Proceed')                return false;            }        }    </script>
    <script language="javascript" type="text/javascript">        function launcher(page) {            movwin = window.open(page, "movwin", "width=600,height=300,top=0,left=0,toolbar=no,scrollbars=yes,resizable=yes,menubar=yes,status=no,directories=no,location=no")        }    </script>
    <script type="text/javascript" language="javascript">
        window.SMC_CHAT_FRAME_URLS = [];

        for (var chatOriginIndex = 0; chatOriginIndex < window.SMC_CHAT_SERVER_ORIGINS.length; chatOriginIndex++) {
            window.SMC_CHAT_FRAME_URLS.push(window.getSmcChatUrl("/widget-embed", chatOriginIndex));
        }

        function setAspxChatVisibility(isOpen) {
            var chatbot = document.getElementById("chatbot");
            var launcher = document.getElementById("chatLauncher");
            var frame = document.getElementById("chatbotFrame");

            if (!chatbot) {
                return;
            }

            chatbot.classList.toggle("chat-hidden", !isOpen);

            if (launcher) {
                launcher.setAttribute("aria-expanded", isOpen ? "true" : "false");
            }

            if (isOpen && frame && !frame.getAttribute("src")) {
                frame.setAttribute("src", window.SMC_CHAT_FRAME_URLS[0]);
            }
        }

        function toggleAspxChat() {
            var chatbot = document.getElementById("chatbot");

            if (!chatbot) {
                return;
            }

            setAspxChatVisibility(chatbot.classList.contains("chat-hidden"));
        }

        function fallbackAspxChatFrame() {
            var frame = document.getElementById("chatbotFrame");
            var currentIndex = parseInt(frame && frame.getAttribute("data-url-index") || "0", 10);
            var nextIndex = currentIndex + 1;

            if (!frame || nextIndex >= window.SMC_CHAT_FRAME_URLS.length) {
                return;
            }

            frame.setAttribute("data-url-index", String(nextIndex));
            frame.setAttribute("src", window.SMC_CHAT_FRAME_URLS[nextIndex]);
        }

        function initializeAspxChatAssets() {
            var frame = document.getElementById("chatbotFrame");
            var logo = document.getElementById("chatLogo");

            if (logo) {
                window.setSmcChatAsset(logo, "src", "/static/logo.png", 0);
            }

            if (frame) {
                frame.setAttribute("data-url-index", "0");
            }
        }

        if (window.addEventListener) {
            window.addEventListener("load", initializeAspxChatAssets);
        } else if (window.attachEvent) {
            window.attachEvent("onload", initializeAspxChatAssets);
        }
    </script>
    <style type="text/css">
        .fontInstn {
            font-family: 'Times New Roman';
            font-size: 10px;
        }

        .blink_me {
            animation: blinker 3s linear infinite;
            color: red;
        }

        @keyframes blinker {
            50% {
                opacity: 0;
            }
        }

        .auto-style1 {
            FONT-FAMILY: 'Times New Roman';
            color: #000000;
            FONT-SIZE: small;
            LETTER-SPACING: normal;
            TEXT-TRANSFORM: none;
            WORD-SPACING: normal;
            text-align: justify;
            font-size: 18px;
        }

        .auto-style2 {
            font-size: small;
            text-align: center;
        }
         .auto-styleSmaller {
            font-size: small;
            text-align: left;
        }

        .auto-style3 {
            text-align: left;
        }

        .auto-style4 {
            font-size: medium;
        }

        .chat-launcher {
            position: fixed;
            right: 20px;
            bottom: 20px;
            z-index: 9998;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 68px;
            height: 68px;
            padding: 0;
            border: 0;
            border-radius: 999px;
            background: linear-gradient(135deg, #1976d2, #42a5f5);
            color: #ffffff;
            box-shadow: 0 20px 40px rgba(25, 118, 210, 0.24);
            cursor: pointer;
            font-family: 'Times New Roman', serif;
            font-size: 14px;
            font-weight: bold;
            letter-spacing: 0.04em;
        }

        .chat-launcher:hover {
            transform: translateY(-1px);
        }

        .smc-chatbot-widget + .chat-launcher {
            display: inline-flex;
        }

        .smc-chatbot-widget:not(.chat-hidden) + .chat-launcher {
            display: none;
        }

        @media (max-width: 640px) {
            .chat-launcher {
                right: 10px;
                bottom: 10px;
            }
        }
    </style>
</head>
<body ms_positioning="GridLayout">
    <form id="frmDefault" method="post" runat="server">
        <table cellpadding="0" cellspacing="0" border="0" width="100%" height="100%" class="TableBorder">
            <tr>
                <td colspan="2" valign="top" height="116">
                   
                </td>
            </tr>
            <tr>
                <td>
                    <table border="0" cellpadding="5" cellspacing="0" width="100%">
                        <tr>
                            <td align="center"><table>
                                    <tr>
                                        <td colspan="2" align="center">
                                            <asp:Label ID="lblerr" runat="server" Font-Bold="True" ForeColor="Red" Font-Names="Verdana"
                                                Font-Size="Small" CssClass="auto-style4"></asp:Label></td>
                                    </tr>
                                    <tr>
                                        <td valign="top" colspan="2">
                                            <ul style="font-family: 'Times New Roman'; text-align: left; font-size: 20px; font-weight: bold;">
                                                Instructions for Submitting the Online Application Form</span>                                           
                                            </ul>
                                            <ul class="auto-style1">
                                                <%--<p class="auto-style">                                                    <b><span class="blink_me"><strong>UG &amp; PG programs are under maintenance and it will be opened shortly.</strong></span></b>                                                </p>--%>
                                                <p>
                                                    Applicants are required to carefully read the instructions given below before submitting the online application form.
                                                </p>
                                                <p>
                                                    The College reserves the right to reject applications that are</p>
                                                <ul>
                                                    <li style="font-size: 18px">Incomplete                                                 </li>
                                                    <li style="font-size: 18px">Incorrect or contain false information                                                 </li>
                                                    <li style="font-size: 18px">Missing mandatory documents</li>
                                                    <li style="font-size: 18px">Submitted without payment of the application fee</li>
                                                </ul>
                                                <p>
                                                    <strong>1. Uploading Required Documents</strong></p>
                                                <p>
                                                    Before submitting the online application form, applicants must upload the following scanned images:                                                                                              
                                                </p>
                                                <ul>
                                                    <P >1. Passport-size photograph in JPG/JPEG format (maximum size: 50 KB)</P>
                                                    <P >2. Applicant’s signature in JPG/JPEG format (maximum size: 20 KB)</p>
                                                    <P >3. Parent/Guardian’s signature in JPG/JPEG format (maximum size: 20 KB)</P>
                                                    <P >4. Community Certificate (except for OC and ‘Others’ categories) in JPG/JPEG/GIF format (maximum size: 2 MB)</P>
                                                    <P >5. Baptism Certificate (only for Catholic applicants) in JPG/JPEG/GIF format (maximum size: 2 MB)                                                    <%--<li style="font-size: 15px">For UG applicants--attested copy of the tenth, eleventh and plus two downloaded mark statements in PDF/JPG/JPEG format of maximum 300 KB</li>--%>
                                                    <P >6. Self-attested copies of all available semester mark sheets (for Postgraduate applicants) compiled into a single PDF (maximum size: 5 MB)                                                    <%--<li style="font-size: 15px">Differently Abled Certificate (only for Differently Abled applicants) in JPG/JPEG/GIF format of maximum 300 KB </li>--%>
                                                </ul>
                                                <p>
                                                    <strong>2. Important Guidelines</strong></p>
                                                <p>
                                                <p>
                                                    &nbsp;&nbsp;&nbsp;1. Documents can be uploaded only after entering academic marks.                                               
                                                </p>
                                                <%-- <p >&nbsp;&nbsp;&nbsp; 4. Hostel Applications will be summarily rejected if local guardian’s name and address are not provided.</p>--%>
                                                <p>
                                                    &nbsp;&nbsp;&nbsp;2. The Unique Application Number (UAN), required for uploading documents, will be generated when the “Save” option is clicked on the Preview page.</span>
                                                <p class="auto-style3">
                                                    &nbsp;&nbsp;&nbsp;3. Use the UAN as the Username and your Date of Birth as the Password to log in and upload documents on the College website.</span>
                                                </p>
                                                <p>
                                                    &nbsp;&nbsp;&nbsp;4. Applicants may edit application details before paying the application fee by clicking the “Login” button.
                                                </p>
                                                <p>
                                                    <strong>&nbsp;&nbsp;&nbsp;5. Editing or updating details will not be possible after the application fee has been paid.</span></strong>
                                                </p>
                                                <%-- <p>                                                    &nbsp;&nbsp;&nbsp; 8. Online payment of application fee will begin immediately after the announcement of Tamil Nadu Higher Secondary School Certificate (TNHSC) results.                                                </p>--%>
                                                <p>
                                                    &nbsp;&nbsp;&nbsp;6. Payment of the application fee must be made online via <strong>internet banking, credit card, or debit card only.</strong>
                                                </p>
                                                <p>
                                                    &nbsp;&nbsp;&nbsp;7. The <strong>application fee is non-refundable</strong> under any circumstances.                                               
                                                </p>
                                                <p>
                                                   &nbsp;&nbsp;&nbsp;8. Applicants can check their application and fee payment status through the Applicant’s login on the College website.                                               
                                                </p>
                                                <p>
                                                   &nbsp;&nbsp;&nbsp;9. The receipt of the application fee will be updated in the Applicant’s login <strong>24 hours</strong> after the transaction.                                               
                                                </p>
                                                <p>
                                                    &nbsp;&nbsp;&nbsp;10. Information regarding applicants shortlisted for interviews will be sent via email and SMS, and uploaded on the College website. <br />&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Applicants must attend the interview on the date and time specified. Being called for an interview does <strong>not</strong> guarantee admission.                                                 
                                                    
                                                 </p>  
                                                <p>
                                                   &nbsp;&nbsp;&nbsp;11. No information will be sent to applicants who are not provisionally selected.                                               
                                                </p>
                                                <p>
                                                   &nbsp;&nbsp;&nbsp;12. The list of provisionally selected applicants will be uploaded on the College website after 8:00 p.m.                                                    <%-- <p class="auto-style3">                                                    &nbsp;15. Applicants called for B.A. English and all postgraduate programmes will have to take an entrance test before the interview is                                                 <br />                                                    <span style="margin-left: 32px">conducted. Applicants called for B.V.A. will have to take an Aptitude Test (drawing/designing) before the interview.</span>                                                </p>--%>
                                                <p>
                                                   &nbsp;&nbsp;&nbsp;13. Selected applicants must pay the prescribed fees and submit their original certificates along with photocopies on the date and time specified.<strong><br />&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Late payments will not be accepted.</strong>                                               
                                                </p>
                                                <p>
                                                    &nbsp;&nbsp;&nbsp;14.  Details about documents required at the time of interview can be accessed by clicking the <strong>Document Info Attachment</strong> button.
                                                </p>
                                                
                                                <%--<p>                                                    &nbsp;17. <strong><span class="blink_me">Hostel facility is not available for this academic year 2024-2025</span></strong>. </p>--%>                                               <%-- <p>                                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <strong>Applicants for undergraduate programmes please note the following: Instructions for criteria for selecting Part I Language can be accessed<br /> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; by clicking on the Language Selection Criteria button.</strong></p>--%>
                                            </ul>
                                        </td>
                                    </tr>
                                    <tr>
                                
                                        <td style="font-family: 'Times New Roman'; font-size: 18px; color: black"  align="left">
                                           
                                    <ul>
                                        <p style="font-weight:bold;font-size:21px;"><strong>Note:</strong></p>
                                        <p>The <strong>application fee is non-refundable.</strong></p>
                                        <p>For further queries, please email : <strong>admissions@stellamariscollege.edu.in</strong></p>
                                </ul>
                                     
                                        </td>
                                    </tr>
                                    <%--<tr>
                                        <td style="font-family: 'Times New Roman'; font-size: 18px; color: black" colspan="2" align="center"><strong>Any further queries may be sent to the following e-mail address:<br />
                                        </strong><span class="blink_me"><strong>admissions@stellamariscollege.edu.in.</strong></span></td>
                                    </tr>--%>
                                    <tr align="left">
                                        <td style="font-weight: bold; font-size: 19px; font-family: 'Times New Roman'; color: black"  class="auto-styleSmaller">&nbsp;                                            <ul><p style="font-weight:bold;font-size:21px;"><strong>Declaration</strong></p></ul>
                                            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<asp:CheckBox ID="Chkagree1" runat="server" />I have carefully read the prospectus, instructions, and eligibility criteria for applying to the programmes offered by the College.</td>
                                    </tr>
                                    <tr align="left">
                                        <td style="font-weight: bold; font-size: 19px; font-family: 'Times New Roman'; color: black" align="center"  colspan="2" class="auto-styleSmaller">
                                            
                                            <span><strong>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<asp:CheckBox ID="chkagree" runat="server" />I understand and agree to abide by the instructions for applying for admission to Stella Maris College.</strong></span>                                        </td>
                                    </tr>
                                    <tr id="trbuttonInstruction" runat="server">
                                        <%--<td align="right" width="50%">--%>
                                        <td align="center">
                                            <div>
                                                <table>
                                                    <tr>
                                                        <td align="right"><a href="StellaMarisCollegeProspectus-UG.pdf" target="_blank">
                                                            <asp:Image ID="ImgUGProspectus" runat="server" ImageUrl="Images/ugprospectus.png" TabIndex="1"></asp:Image></a>                                        </td>
                                                        <td align="center"><a href="StellaMarisCollegeProspectus-PG.pdf" target="_blank">
                                                            <asp:Image ID="ImgPGProspectus" runat="server" ImageUrl="Images/pgprospectus.png" TabIndex="2"></asp:Image></a>                                        </td>
                                                        <td align="left" ><a href="StellaMarishostel.pdf" target="_blank">
                                                            <asp:Image ID="prospectus1" runat="server" ImageUrl="Images/hostelprospectus.gif" TabIndex="3"></asp:Image></a>                                        </td>
                                                    </tr>
                                                </table>
                                            </div>
                                        </td>
                                        <%--<tr id="tr1" runat="server">--%>
                                        <%--<td align="right" width="50%">--%>
                                        <%--<td align="right"  width="50%" >
                                            <a href="StellaMarisCollegeProspectus-UG.pdf" target="_blank">
                                                <asp:Image ID="ImgUGProspectus" runat="server" ImageUrl="Images/ugprospectus.png" TabIndex="1"></asp:Image></a>
                                        </td>
                                        <td align="left" colspan="2" width="50%">
                                            <a href="StellaMarisCollegeProspectus-PG.pdf" target="_blank">
                                                <asp:Image ID="ImgPGProspectus" runat="server" ImageUrl="Images/pgprospectus.png" TabIndex="2"></asp:Image></a>
                                            <a href="StellaMarishostel.pdf" target="_blank">
                                                <asp:Image ID="prospectus1" runat="server" ImageUrl="Images/hostelprospectus.gif" TabIndex="2"></asp:Image></a>
                                        </td>--%>
                                        
                                    </tr>
                        </tr>
                        <tr id="trApply" runat="server" style="display: none;">
                            <td colspan="3" align="center">
                                <asp:ImageButton ID="ImageButton1" runat="server" ImageUrl="~/Images/document-info.png" TabIndex="4"></asp:ImageButton>
                                <a href="LanguageSelection.pdf" target="_blank">
                                    <asp:Image ID="ImgLsc" runat="server" ImageUrl="~/Images/language-selection-criteria.png" TabIndex="5"></asp:Image></a>                                        </td>
                        </tr>
                        <tr id="trApplicantLogin" runat="server">
                            <td colspan="3" align="center">
                                <asp:ImageButton ID="ImgBtnApplyOnline" runat="server" ImageUrl="Images/applyOnline.gif" TabIndex="6" OnClientClick="return ValidateForm();"></asp:ImageButton>
                                <asp:ImageButton ID="ImgAppLoginPage" runat="server" ImageUrl="Images/application-login-page.png" TabIndex="7"></asp:ImageButton>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
        </td>
            </tr>
            <tr height="30" align="center">
                <td colspan="2" bgcolor="#ffffff">
                 
                </td>
            </tr>
        <%-- </table>--%>

        <div id="chatbot" class="smc-chatbot-widget chat-hidden">
            <div class="chat-header">
                <div class="chat-brand">
                    <img id="chatLogo" alt="Stella Maris College logo" class="chat-logo" />
                    <span>Stella Maris College (Autonomous)</span>
                </div>
                <button onclick="toggleAspxChat()" class="close-btn" type="button" aria-label="Close chat">x</button>
            </div>

            <iframe
                id="chatbotFrame"
                class="chat-frame"
                title="Stella Maris College chatbot"
                loading="lazy"
                onerror="fallbackAspxChatFrame()"
                referrerpolicy="no-referrer-when-downgrade"></iframe>
        </div>

        <button id="chatLauncher" class="chat-launcher" type="button" onclick="toggleAspxChat()" aria-controls="chatbot" aria-expanded="false" aria-label="Open chat">
            Chat
        </button>
    </form>
</body>
</html>
