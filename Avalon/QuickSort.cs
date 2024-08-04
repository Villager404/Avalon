namespace Avalon
{
    internal class QuickSort
    {
        public static void Sort(int[] array, int low, int high)
        {
            if (low < high)
            {
                // Partition the array
                int pi = Partition(array, low, high);

                // Recursively sort elements before and after partition
                Sort(array, low, pi - 1);
                Sort(array, pi + 1, high);
            }
        }

        static int Partition(int[] array, int low, int high)
        {
            // Choose the rightmost element as pivot
            int pivot = array[high];
            int i = (low - 1); // Index of smaller element

            for (int j = low; j < high; j++)
            {
                // If the current element is smaller than or equal to the pivot
                if (array[j] <= pivot)
                {
                    i++;

                    // Swap array[i] and array[j]
                    Swap(array, i, j);
                }
            }

            // Swap the pivot element with the element at index i + 1
            Swap(array, i + 1, high);

            return i + 1;
        }

        static void Swap(int[] array, int i, int j)
        {
            int temp = array[i];
            array[i] = array[j];
            array[j] = temp;
        }
    }
}
