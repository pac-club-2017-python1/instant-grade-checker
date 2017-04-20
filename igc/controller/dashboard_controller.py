import random

from flask import redirect
from flask import request

from igc.controller import auth_controller
from igc.controller.biometrics import scanner
from igc.util.util import session_scope
from igc.util.cache import students, cacheStudentData

def controller(app, models, db):

    template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
        <meta name="description" content="">
        <meta name="author" content="">
        <link rel="icon" href="favicon.ico">
    
        <title>Student Information System</title>
    
        <!-- Bootstrap core CSS -->
        <link href="../../static/bower_components/bootstrap/dist/css/bootstrap.min.css" rel="stylesheet">
    
    </head>
    
    <body>
    <div class="jumbotron">
        <div class="container">
            <h1 class="display-3">Dashboard</h1>
            <p>{full_name}</p>
            <button id="logout" class="btn btn-danger btn-lg">Logout</button>
        </div>
    </div>
    
    <div class="container">
        <div class="row" style='padding-bottom: 10px'>
            <button id="recordFingerprint" class="btn btn-success btn-lg">Record/Update your Fingerprint</button>
        </div>
        
        <div class="row">
            <table class="table table-hover table-bordered">
                <thead>
                    {table_headers}
                </thead>
                <tbody>
                    {table_body}
                </tbody>
            </table>
        </div>
    
        <hr>
    
        <footer>
            <p>&copy; VBCPS 2017</p>
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
            <button id="startFingerprint" class="btn btn-success btn-lg">Start</button>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>
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
        $("#logout").click(function(e){
            location.pathname = "/index.html"
            location.search = ""
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

                if students[user.student_id]["table_body"] is None:
                    cacheStudentData(user.student_id, students[user.student_id])

                cache = students[user.student_id]
                string = string.replace("{full_name}", cache["full_name"])
                string = string.replace("{table_headers}", cache["welcome_message"])
                string = string.replace("{table_body}", cache["table_body"])
                return string
            else:
                return redirect("index.html?reason=login", code=302)

    @app.route("/api/enrollFp")
    def enroll_fingerprint():
        User = models["user"]
        token = request.args.get('token')
        with session_scope(db) as session:
            user = session.query(User).filter(User.token == token).first()
            if user:
                success, fid = scanner.enroll()
                print success, fid
                if success:
                    user.fingerprint_id = fid
                    return "OK"
                else:
                    return "Error: Please try again"
            else:
                return "Error: Authentication problem"

    @app.route("/api/identifyFp")
    def identify_fingerprint():
        User = models["user"]
        with session_scope(db) as session:
            success, target = scanner.identify()
            if success:
                user = session.query(User).filter(User.fid == target).first()
                if int(user.student_id) in auth_controller.user_keys:
                    tokengen = ''.join(random.choice('0123456789ABCDEF') for i in range(16))
                    tokengen = user.student_id + "_" + tokengen
                    user.token = tokengen
                    return "OK;" + tokengen
                else:
                    return "Error: You must log in once manually with your PIN before using the scanner"
            else:
                return "Error: No fingerprint identified"