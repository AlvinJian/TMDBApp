package movie.controller;

import java.io.IOException;
import java.text.DateFormat;
import java.text.DecimalFormat;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;

import org.controlsfx.control.Rating;

import javafx.beans.binding.Bindings;
import javafx.event.ActionEvent;
import javafx.event.EventHandler;
import javafx.fxml.FXML;
import javafx.fxml.FXMLLoader;
import javafx.scene.control.Button;
import javafx.scene.control.Hyperlink;
import javafx.scene.control.Label;
import javafx.scene.control.ListCell;
import javafx.scene.control.ListView;
import javafx.scene.control.TableColumn;
import javafx.scene.control.TableView;
import javafx.scene.control.TextArea;
import javafx.scene.control.TextField;
import javafx.scene.control.cell.PropertyValueFactory;
import javafx.scene.image.ImageView;
import javafx.scene.layout.AnchorPane;
import javafx.scene.layout.BorderPane;
import javafx.scene.text.Text;
import javafx.scene.text.TextAlignment;
import javafx.scene.text.TextFlow;
import javafx.util.Callback;
import javafx.util.converter.NumberStringConverter;
import movie.Main;
import movie.database.DBHandler;
import movie.database.MovieTuple;
//import movie.database.MovieTuple.Compact;

public class MovieInfoController {
	@FXML
	private Text movieName;
	 @FXML
    private TableView<String> infoTable;

	@FXML
    private ListView<String> nameCol;

    @FXML
    private ListView<AnchorPane> valCol;
    
    @FXML
    private Button backButton;

    
    @FXML
    private BorderPane moviePane;
    
    @FXML
    private ImageView movieImg;
    
    @FXML
    private AnchorPane imgPane;
    
   // @FXML
//    private AnchorPane title;

	@FXML
	public void initialize() throws IOException {
			}
	private void loadReviews() throws IOException {
		FXMLLoader loader = new FXMLLoader();
		loader.setLocation(Main.class.getResource("view/Review.fxml"));
		AnchorPane reviewScene = loader.load();
		ReviewController controller = loader.<ReviewController>getController();			
		controller.getReviewsByMovie(movieID);
		controller.loadMovieReviews();
		moviePane.setRight(reviewScene);
	}
	public void getMovieInfo(MovieTuple.Compact mv) throws IOException {
		//genreID = mv);
		movieID = mv.getId();
	//	System.out.println("2/reviews for movieID in movieinfo:" + movieID);
		
		DBHandler db = new DBHandler();
		MovieTuple movieInfo = db.getMovieById(mv.getId());
		movieImg.setImage(db.tryGetMovieImage(mv.getId()));
		movieImg.setFitHeight(300);
		
//		movieImg.fitWidthProperty().bind(imgPane.widthProperty());
//		movieImg.fitHeightProperty().bind(imgPane.heightProperty());
		String overview = movieInfo.getOverview();
//		genreID = movieInfo.getGenres(); this is a list
		movieName.setText(mv.getTitle());
		
		nameCol.getItems().add("Rating");
		nameCol.getItems().add("Overview");
		nameCol.getItems().add("Release Date");
		nameCol.getItems().add("Popularity");
		nameCol.getItems().add("Actors");
		Rating rating  = new Rating();
	    rating.setPartialRating(true);
	    rating.setRating(mv.getVoteAverage()/2);
	    rating.setDisable(true);
	
	    AnchorPane anchorPane1 = new AnchorPane();
	    Label label1 = new Label(String.valueOf(mv.getVoteAverage()));
	    anchorPane1.getChildren().addAll(rating,label1);
	    anchorPane1.setTopAnchor(rating, 1.0);
	    anchorPane1.setBottomAnchor(label1, 1.0);
		    
		valCol.getItems().add(anchorPane1);
		
		AnchorPane anchorPane2 = new AnchorPane();
		 Label label2 = new Label(overview);
		 
		// label2.maxWidth(100);
		 label2.setWrapText(true);
		 label2.setTextAlignment(TextAlignment.JUSTIFY);
		 label2.setStyle("-fx-max-width:400px");
		// System.out.println("width: "+label2.prefWidthProperty().getValue());
		anchorPane2.getChildren().add(label2);
		valCol.getItems().add(anchorPane2);

		
		DateFormat df = new SimpleDateFormat("MM/dd/yyyy");
		Date releaseDate = mv.getReleaseDate();
		AnchorPane anchorPane3 = new AnchorPane();
		 Label label3 = new Label(df.format(releaseDate));
		anchorPane3.getChildren().add(label3);
		valCol.getItems().add(anchorPane3);

		AnchorPane anchorPane4 = new AnchorPane();
		DecimalFormat numberFormat = new DecimalFormat("#");
	    Label label4 = new Label(String.valueOf(numberFormat.format(mv.getPopularity())));
	    anchorPane4.getChildren().add(label4);
		valCol.getItems().add(anchorPane4);
		
		TextFlow flow = new TextFlow();
		List<MovieTuple.Cast> casts = db.getCastsByMovie(mv.getId()); 
    	for(MovieTuple.Cast c: casts) {
    		Hyperlink link = new Hyperlink(c.getActor().getActorName());
			link.setOnAction(new EventHandler<ActionEvent>() {
			    @Override
			    public void handle(ActionEvent e) {
			    	e.getSource();
			      try {
					Main.showActorInfoScene(c.getActor());
					} catch (IOException e1) {
						e1.printStackTrace();
					};
			    }
			});
			flow.getChildren().add(link);
			flow.getChildren().add(new Text(" ,"));
			
		}
    	flow.setStyle("-fx-max-width:400px");
    	AnchorPane anchorPane5 = new AnchorPane();
    	anchorPane5.getChildren().add(flow);
  		valCol.getItems().add(anchorPane5);
  		
//		valCol.setCellFactory(new Callback<ListView<AnchorPane>, ListCell<AnchorPane>>() {
//            @Override
//            public ListCell<AnchorPane> call(final ListView<AnchorPane> list) {
//                return new ListCell<AnchorPane>() {
//                    {
//                        Text text = new Text();
//                        text.wrappingWidthProperty().bind(list.widthProperty().subtract(15));
//                        text.textProperty().bind(itemProperty());
//
//                        setPrefWidth(0);
//                        setGraphic(text);
//                    }
//                };
//            }
//        });
		loadReviews();
	}
	String genreID,movieID = new String() ;
	@FXML
	private void goToMainPage() throws IOException {
//		Main.showMoviesByGenre(genreID);
		Main.showMainViewScene();
	}
	
//	@FXML
//	private void goToReview() throws IOException {
//		Main.showReviewScene(movieID);
//	}
}
