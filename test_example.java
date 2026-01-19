public class Example {
    public int calculateSum(int[] numbers) {
        int sum = 0;
        for (int i = 0; i < numbers.length; i++) {
            sum = sum + numbers[i];
        }
        return sum;
    }

    public String classify(int score) {
        String grade;
        if (score >= 90) {
            grade = "A";
        } else if (score >= 80) {
            grade = "B";
        } else {
            grade = "C";
        }
        return grade;
    }

    public int findMax(int a, int b) {
        if (a > b) {
            return a;
        }
        return b;
    }
}
