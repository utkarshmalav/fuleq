const admin = require("firebase-admin");
const fs = require("fs");
const path = require("path");
const { setTimeout } = require("timers/promises");  // For creating delay

// Initialize Firebase Admin SDK
const serviceAccount = require("./serviceAccountKey.json");  // Use forward slash or double backslash
admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
  storageBucket: "fuelq-864ff.appspot.com",  // Replace with your actual Firebase project ID
});

const bucket = admin.storage().bucket();
const folderPath = "./frames";
const imagesFolder = "images/";

// Function to get the timestamp from the file's name and convert it into a Date object
function getFileTime(fileName) {
  // Extract the time part: "01-16-03_14-11-2024" (after the first underscore and before the second)
  const timePart = fileName.split('_')[1];
  const [hour, minute, second] = timePart.split('-');
  
  // Extract the date part: "14-11-2024" (after the second underscore)
  const datePart = fileName.split('_')[2].replace('.jpg', '');
  const [day, month, year] = datePart.split('-');

  // Create and return a Date object using extracted values
  return new Date(year, month - 1, day, hour, minute, second);  // Months are 0-based in JavaScript Date
}

// Function to list all files in Firebase storage folder and delete the oldest if there are more than 15 images
async function manageFirebaseImages() {
  const [files] = await bucket.getFiles({ prefix: imagesFolder });
  
  if (files.length >= 15) {
    // Sort files by the creation time (oldest first)
    files.sort((a, b) => a.metadata.timeCreated - b.metadata.timeCreated);

    // Delete the oldest file
    const oldestFile = files[0];
    await oldestFile.delete();
    console.log(`Deleted the oldest file: ${oldestFile.name}`);
  }
}

// Upload images
fs.readdir(folderPath, async (err, files) => {
  if (err) return console.error("Unable to read folder:", err);

  // Filter for images starting with 'C'
  const imagesToUpload = files.filter(file => file.startsWith('C'));

  // Sort images by the timestamp in the filename (oldest first)
  imagesToUpload.sort((a, b) => getFileTime(a) - getFileTime(b));

  for (const file of imagesToUpload) {
    const filePath = path.join(folderPath, file);
    const vehicleCount = path.basename(file, path.extname(file)).split('_')[0].slice(1); // Extract count (before the underscore)

    try {
      // Manage Firebase image storage (limit to 15 images)
      await manageFirebaseImages();

      // Upload the image
      await bucket.upload(filePath, {
        destination: `${imagesFolder}${file}`,
      });

      console.log(`Uploaded ${file} with vehicle count: ${vehicleCount}`);

      // After uploading, delete the file from the folder
      fs.unlink(filePath, (err) => {
        if (err) console.error("Error deleting file:", err);
        else console.log(`Deleted ${file} from the folder.`);
      });

      // Wait for 5 seconds before uploading the next image
      await setTimeout(5000);  // 5 seconds delay

    } catch (err) {
      console.error("Error uploading image:", err);
    }
  }
});
