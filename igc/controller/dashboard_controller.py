import random

from flask import redirect
from flask import request

from igc.controller import auth_controller
from igc.util.util import session_scope
from igc.util.cache import getStudent, cacheStudentData

def controller(app, models, db):

    template = \
    """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
        <meta name="description" content="">
        <meta name="author" content="">
        
        <!-- Disable caching -->
        <meta http-equiv="cache-control" content="max-age=0" />
        <meta http-equiv="cache-control" content="no-cache" />
        <meta http-equiv="expires" content="0" />
        <meta http-equiv="expires" content="Tue, 01 Jan 1980 1:00:00 GMT" />
        <meta http-equiv="pragma" content="no-cache" />
        
        <link rel="icon" href="favicon.ico">
    
        <title>Student Information System</title>
    
        <!-- Bootstrap core CSS -->
        <link href="bower_components/bootstrap/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="css/responsive_table.css" rel="stylesheet">
        <!-- <link href="https://fonts.googleapis.com/css?family=Open+Sans" rel="stylesheet"> -->
        <link href="css/custom.css" rel="stylesheet">
        <script src="startsWith.js"></script>
    </head>
    
    <body onhashchange="onhashchange();">
    
    <!--
    <div class="jumbotron">
        <div class="container">
            <h1 class="display-3">Dashboard</h1>
            <p>{full_name}</p>
        </div>
    </div>
    -->
    
    <div class="container">
        <div class="row" style='padding-bottom: 10px; visibility: {allow_fingerprint}'>
            <button id="logout" class="btn btn-danger btn-lg">Logout</button>
            <button id="recordFingerprint" class="btn btn-success btn-lg">Record/Update your Fingerprint</button>
        </div>
        
        <div class="row">
            <ul class="nav nav-tabs">
              <li role="presentation" id="tab-grades"><a href="#grades" class="links" id="link-grades">Grades</a></li>
              <li role="presentation" id="tab-class_schedule"><a href="#class_schedule" class="links" id="link-class_schedule">Class Schedule</a></li>
            </ul>
            <div class="panel panel-default" id="panel-grades" style="visibility: hidden;">
              <table class="table table-hover table-mc-light-blue">
                    <thead>
                        {table_headers}
                    </thead>
                    <tbody>
                        {table_body}
                    </tbody>
                </table>
            </div>
            <div class="panel panel-default" id="panel-class_schedule" style="visibility: hidden;">
              <table class="table table-hover table-mc-light-blue">
                    {class_schedule}
                </table>
            </div>
        </div>  
        <hr>
        <footer>
            <p>&copy; Yoland Gao, Dylan Win, Tanmay Parakala-Jain, Chris Giroud 2017</p>
        </footer>
    </div> <!-- /container -->
    
    
    <div class="modal fade" tabindex="-1" role="dialog" id="fingerprintModal">
      <div class="modal-dialog" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
            <h4 class="modal-title">Record Fingerprint</h4>
          </div>
          <div class="modal-body">
            <p>Press your finger on the scanner, and hold until the scanner light turns off.</p>
            <hr>
            <button id="startFingerprint" class="btn btn-success btn-lg">Start</button>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-default btn-lg" data-dismiss="modal">Close</button>
          </div>
        </div><!-- /.modal-content -->
      </div><!-- /.modal-dialog -->
    </div><!-- /.modal -->
    
    <!-- Bootstrap core JavaScript
    ================================================== -->
    <!-- Placed at the end of the document so the pages load faster -->
    <script src="../../static/bower_components/jquery/dist/jquery.min.js"></script>
    <script src="../../static/bower_components/bootstrap/dist/js/bootstrap.min.js"></script>
    <script src="../../static/bower_components/bootstrap-validator/dist/validator.min.js"></script>
    <link href="../../static/bower_components/toastr/toastr.min.css" rel="stylesheet">
    <script src="../../static/bower_components/toastr/toastr.min.js"></script>
    <script>
        $(document).ready(function(e){
            if(location.hash.trim() === ""){
                location.hash = "grades";
            }
        });
        
        function onhashchange(){
            $(".links").each(function(){
                panel = this.id.split("-")[1];
                console.log(panel);
                
                if(location.hash.replace("#", "").trim() === panel){
                    $("#panel-" + panel).css('visibility', 'visible');
                    $("#panel-" + panel).css('display', 'block');
                    $("#tab-" + panel).addClass("active");
                }else{
                    $("#panel-" + panel).css('visibility', 'hidden');
                    $("#panel-" + panel).css('display', 'none');
                    $("#tab-" + panel).removeClass("active");
                }
            });
        }
        
        $("#logout").click(function(e){
            window.location = "/index.html?token=logout#logout";
        });
        
        $("#recordFingerprint").click(function(e){
            $("#fingerprintModal").modal('show');
        });
        
        $("#startFingerprint").click(function(e){
           $.get("http://127.0.0.1:5000/api/enrollFp?token=" + getParameterByName("token"), function( data ) {
              $("#fingerprintModal").modal('hide');
              if(data !== "OK"){
                 toastr.error(data, "Message");
              }else{
                 toastr.success("Successfully enrolled fingerprint", "Success");
              }
           });
        });
    
        function getParameterByName(name, url) {
            if (!url) url = window.location.href;
            name = name.replace(/[\[\]]/g, "\\$&");
            var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
                results = regex.exec(url);
            if (!results) return null;
            if (!results[2]) return '';
            return decodeURIComponent(results[2].replace(/\+/g, " "));
        }
    </script>
    </body>
    </html>
    """


    @app.route("/dashboard.html")
    def dashboard():
        User = models["user"]
        token = request.args.get('token')
        with session_scope(db) as session:
            user = session.query(User).filter(User.token == token).first()
            if user and int(user.student_id) in auth_controller.user_keys:
                string = template

                if getStudent(user.student_id)["table_body"] is None:
                    confirmedIncorrect = cacheStudentData(user.student_id, getStudent(user.student_id))
                    if confirmedIncorrect:
                        return redirect("changePassword.html", code=302)


                cache = getStudent(user.student_id)
                string = string.replace("{full_name}", cache["full_name"])
                string = string.replace("{table_headers}", cache["table_headers"])
                string = string.replace("{table_body}", cache["table_body"])
                string = string.replace("{class_schedule}", cache["class_schedule"])
                string = string.replace("{allow_fingerprint}", "visible;" if user.allowFingerprint else "hidden;display: none;")
                return string
            else:
                return redirect("index.html#login", code=302)


    @app.route("/api/enrollFp")
    def enroll_fingerprint():
        User = models["user"]
        token = request.args.get('token')
        with session_scope(db) as session:
            user = session.query(User).filter(User.token == token).first()
            if user:
                from igc.controller.biometrics import scanner
                success, fid = scanner.enroll()
                print success, fid
                if success:
                    user.fid = fid
                    return "OK"
                else:
                    return "Error: Please try again"
            else:
                return "Error: Authentication problem"

    @app.route("/api/allowFingerprintStatus")
    def fingerprint_status():
        User = models["user"]
        token = request.args.get('token')
        with session_scope(db) as session:
            user = session.query(User).filter(User.token == token).first()
            allowFingerprint = request.args.get('allowFingerprint')

            #For purposes of our demonstration/pilot program, allow all
            allowFingerprint = True

            if user and allowFingerprint:
                user.allowFingerprint = allowFingerprint
                return "OK"
            else:
                return "Error: Authentication problem"


    @app.route("/api/identifyFp")
    def identify_fingerprint():
        from igc.controller.biometrics import scanner
        User = models["user"]
        with session_scope(db) as session:
            success, target = scanner.identify()
            if success:
                user = session.query(User).filter(User.fid == target).first()
                if user:
                    if user.needsUpdate:
                        return "Change;"
                    if int(user.student_id) in auth_controller.user_keys:
                        tokengen = ''.join(random.choice('0123456789ABCDEF') for i in range(16))
                        tokengen = str(user.student_id) + "_" + tokengen
                        user.token = tokengen
                        user.times = user.times + 1
                        return "OK;" + tokengen
                    else:
                        return "Error: You must log in once manually with your PIN before using the scanner"
            else:
                return "Error: No fingerprint identified"