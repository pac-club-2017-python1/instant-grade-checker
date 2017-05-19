import javafx.application.Application;
import javafx.scene.Scene;
import javafx.scene.input.KeyCode;
import javafx.scene.input.KeyCodeCombination;
import javafx.scene.input.KeyCombination;
import javafx.scene.layout.BorderPane;
import javafx.scene.web.WebEngine;
import javafx.scene.web.WebView;
import javafx.stage.Stage;


/**
 * Created by Yoland Gao on 5/19/17.
 *
 * Instant Grade Checker Bootloader
 */
public class IGC extends Application{


    public void start(Stage primaryStage) throws Exception {
        WebView view = new WebView();
        WebEngine engine = view.getEngine();
        primaryStage.setScene(new Scene(new BorderPane(view)));
        primaryStage.setWidth(800);
        primaryStage.setHeight(600);
        primaryStage.setFullScreenExitHint("");
        primaryStage.setFullScreenExitKeyCombination(new KeyCodeCombination(KeyCode.Q, new KeyCombination.Modifier[]{KeyCombination.CONTROL_DOWN, KeyCombination.ALT_ANY}));
        engine.load("http://127.0.0.1:5000");
        primaryStage.setFullScreen(true);
        view.setContextMenuEnabled(false);
        primaryStage.show();
    }

    public static void main(String[] args){
        launch(args);
    }
}
